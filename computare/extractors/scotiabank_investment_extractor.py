"""
Scotiabank Investment (iTRADE) PDF extractor.

Extracts money movements from Scotia iTRADE investment account statements:
- DEPOSIT / CONTRIBUTION (money in)
- WITHDRAWAL (money out)
- BUY (purchase securities - reduces cash)
- SELL (sell securities - increases cash)
- DIVIDEND / DISTRIBUTION (income)

This focuses on transactions that affect your actual money flow, not just
market value changes.
"""

import re
from pathlib import Path
from typing import List, Optional, Dict
from datetime import date
from dataclasses import dataclass

import pdfplumber

from .base import BaseExtractor
from ..models import (
    Transaction, TransactionType, ExtractionResult,
    StatementMetadata, ExtractionMethod
)


@dataclass
class InvestmentTransaction:
    """Intermediate representation for investment transactions."""
    date_str: str
    activity: str  # BUY, SELL, DEPOSIT, WITHDRAWAL, DIVIDEND, etc.
    description: str
    quantity: Optional[float]
    price: Optional[float]
    amount: float  # Credit/Debit amount
    row_top: float


class ScotiabankInvestmentExtractor(BaseExtractor):
    """
    Extracts transactions from Scotiabank iTRADE investment statements.

    Focuses on cash movements:
    - Deposits/Contributions (money in)
    - Withdrawals (money out)
    - Buy orders (cash -> securities)
    - Sell orders (securities -> cash)
    - Dividends/Distributions (income)
    """

    MONTHS = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
        'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
        'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }

    # Activity types we care about
    CASH_ACTIVITIES = {
        'BUY', 'SELL', 'DEPOSIT', 'WITHDRAW', 'WITHDRAWAL', 'CONTRIBUTION',
        'DIVIDEND', 'DISTRIBUTION', 'INTEREST', 'FEE', 'TRANSFER'
    }

    # Column boundaries (based on PDF analysis)
    # Date | Activity | Description | Quantity | Price | Credit/Debit(-)
    COLUMNS = {
        'date_max': 80,          # Date column ends
        'activity_max': 130,     # Activity column ends
        'description_max': 400,  # Description ends
        'quantity_max': 445,     # Quantity ends
        'price_max': 510,        # Price ends
        'amount_min': 510,       # Amount starts
    }

    def can_handle(self, pdf_path: str | Path) -> bool:
        """Check if this is a Scotiabank iTRADE investment statement."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) == 0:
                    return False
                text = pdf.pages[0].extract_text() or ""

                is_itrade = "scotiaitrade" in text.lower() or "itrade" in text.lower()
                is_investment = "investment" in text.lower() or "portfolio" in text.lower()
                has_account_num = "AccountNumber" in text.replace(" ", "") or "Account Number" in text

                return is_itrade and is_investment and has_account_num
        except Exception:
            return False

    def extract(self, pdf_path: str | Path, year: Optional[int] = None) -> ExtractionResult:
        """Extract transactions from Scotiabank iTRADE PDF."""
        pdf_path = Path(pdf_path)
        year = year or self._detect_year_from_filename(pdf_path.name)
        statement_month = self._detect_month_from_filename(pdf_path.name)

        all_transactions: List[Transaction] = []
        raw_transactions: List[InvestmentTransaction] = []

        metadata = StatementMetadata(bank="Scotiabank iTRADE")

        with pdfplumber.open(pdf_path) as pdf:
            # Extract metadata from first page
            if pdf.pages:
                first_page_text = pdf.pages[0].extract_text() or ""

                # Extract account type (TFSA, RRSP, etc.)
                account_type_match = re.search(r'AccountType:\s*(\S+)', first_page_text.replace(" ", ""))
                if account_type_match:
                    metadata.account_type = account_type_match.group(1)

                # Extract statement period
                period_match = re.search(
                    r'ForthePeriod:\s*([A-Z][a-z]+\d+to\d+,\d{4})',
                    first_page_text.replace(" ", "")
                )
                if period_match:
                    metadata.statement_period = period_match.group(1)

                # Try to get net asset value
                nav_match = re.search(r'NetAssetValue[^\$]*\$([\d,]+)', first_page_text.replace(" ", ""))
                if nav_match:
                    try:
                        metadata.closing_balance = float(nav_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            # Process each page looking for Monthly Activity section
            for page in pdf.pages:
                page_transactions = self._extract_transactions_from_page(page, year, statement_month)
                raw_transactions.extend(page_transactions)

        # Convert to Transaction objects
        for raw in raw_transactions:
            trans = self._convert_to_transaction(raw, year, statement_month)
            if trans:
                all_transactions.append(trans)

        # Calculate confidence
        confidence = 1.0 if all_transactions else 0.0

        return ExtractionResult(
            transactions=all_transactions,
            metadata=metadata,
            extraction_method=ExtractionMethod.PDFPLUMBER,
            confidence_score=confidence,
            source_file=str(pdf_path)
        )

    def _extract_transactions_from_page(
        self, page, year: int, statement_month: Optional[int]
    ) -> List[InvestmentTransaction]:
        """Extract transactions from a single page."""
        transactions = []
        words = page.extract_words()

        if not words:
            return transactions

        text = page.extract_text() or ""

        # Only process pages with Monthly Activity section
        if "Monthly Activity" not in text and "MonthlyActivity" not in text.replace(" ", ""):
            return transactions

        # Find the Monthly Activity section boundaries
        activity_start = None
        activity_end = None

        for w in words:
            if w['text'] == 'Monthly' or w['text'] == 'MonthlyActivity':
                activity_start = w['top']
            # End markers
            if activity_start and w['top'] > activity_start + 20:
                if 'Closing' in w['text'] and 'Cash' in text:
                    activity_end = w['top'] + 20  # Include the closing balance line
                    break
                if 'Trades' in w['text'] and 'Settle' in text:
                    activity_end = w['top']
                    break
                if 'Summary' in w['text']:
                    activity_end = w['top']
                    break

        if activity_start is None:
            return transactions
        if activity_end is None:
            activity_end = float('inf')

        # Group words by row
        rows = self._group_words_by_row(words, activity_start + 30, activity_end)

        # Process each row
        for row_top, row_words in sorted(rows.items()):
            transaction = self._parse_transaction_row(row_words, row_top)
            if transaction:
                transactions.append(transaction)

        return transactions

    def _group_words_by_row(
        self, words: List[dict], min_top: float, max_top: float
    ) -> Dict[float, List[dict]]:
        """Group words into rows based on Y position."""
        rows = {}
        tolerance = 3

        for word in words:
            if word['top'] <= min_top or word['top'] >= max_top:
                continue

            # Find existing row or create new one
            found_row = None
            for row_top in rows.keys():
                if abs(word['top'] - row_top) <= tolerance:
                    found_row = row_top
                    break

            if found_row:
                rows[found_row].append(word)
            else:
                rows[word['top']] = [word]

        # Sort words within each row by x position
        for row_top in rows:
            rows[row_top] = sorted(rows[row_top], key=lambda w: w['x0'])

        return rows

    def _parse_transaction_row(
        self, row_words: List[dict], row_top: float
    ) -> Optional[InvestmentTransaction]:
        """Parse a row of words into an InvestmentTransaction."""
        if not row_words:
            return None

        cols = self.COLUMNS

        date_str = ""
        activity = ""
        description_parts = []
        quantity = None
        price = None
        amount = None

        for word in row_words:
            x = word['x0']
            text = word['text']

            if x < cols['date_max']:
                # Date column (e.g., "Jun.02", "May.28")
                if re.match(r'^[A-Z][a-z]{2}\.\d{1,2}$', text):
                    date_str = text
            elif x < cols['activity_max']:
                # Activity column
                if text.upper() in self.CASH_ACTIVITIES or any(
                    act in text.upper() for act in self.CASH_ACTIVITIES
                ):
                    activity = text.upper()
            elif x < cols['description_max']:
                # Description column
                description_parts.append(text)
            elif x < cols['quantity_max']:
                # Quantity column
                try:
                    quantity = float(text.replace(',', ''))
                except ValueError:
                    pass
            elif x < cols['price_max']:
                # Price column
                try:
                    price = float(text.replace(',', ''))
                except ValueError:
                    pass
            else:
                # Amount column
                cleaned = text.replace(',', '').replace('$', '')
                try:
                    amount = float(cleaned)
                except ValueError:
                    pass

        # Skip rows without an activity type we care about
        if not activity:
            return None

        # For BUY/SELL with quantity and price but no amount, the fees ate the proceeds
        # Set amount to 0 so we still track the position change
        if amount is None:
            if activity in ('BUY', 'SELL') and quantity is not None and price is not None:
                amount = 0.0
            else:
                # Skip rows without an amount (header rows, etc.)
                return None

        return InvestmentTransaction(
            date_str=date_str,
            activity=activity,
            description=' '.join(description_parts),
            quantity=quantity,
            price=price,
            amount=amount,
            row_top=row_top
        )

    def _convert_to_transaction(
        self,
        raw: InvestmentTransaction,
        year: int,
        statement_month: Optional[int] = None
    ) -> Optional[Transaction]:
        """Convert InvestmentTransaction to Transaction object."""

        # Parse date (format: "Jun.02")
        date_match = re.match(r'^([A-Z][a-z]{2})\.(\d{1,2})$', raw.date_str)
        if not date_match:
            return None

        month_abbr = date_match.group(1)
        day = int(date_match.group(2))
        month = self.MONTHS.get(month_abbr)

        if not month:
            return None

        # Handle year boundary
        actual_year = year
        if statement_month is not None:
            if statement_month == 1 and month == 12:
                actual_year = year - 1
            elif statement_month == 12 and month == 1:
                actual_year = year + 1

        try:
            trans_date = date(actual_year, month, day)
        except ValueError:
            return None

        # Determine transaction type and amount sign
        # Positive amount = money coming in (deposits, sells, dividends)
        # Negative amount = money going out (withdrawals, buys)
        activity = raw.activity
        amount = raw.amount

        if activity in ('BUY',):
            trans_type = TransactionType.DEBIT
            # Buys are shown as negative in the PDF
            amount = -abs(amount) if amount > 0 else amount
        elif activity in ('SELL',):
            trans_type = TransactionType.CREDIT
            amount = abs(amount)
        elif activity in ('DEPOSIT', 'CONTRIBUTION'):
            trans_type = TransactionType.CREDIT
            amount = abs(amount)
        elif activity in ('WITHDRAW', 'WITHDRAWAL'):
            trans_type = TransactionType.DEBIT
            # Withdrawals are shown as negative in PDF, keep negative
            amount = -abs(amount) if amount > 0 else amount
        elif activity in ('DIVIDEND', 'DISTRIBUTION', 'INTEREST'):
            trans_type = TransactionType.CREDIT
            amount = abs(amount)
        elif activity in ('FEE',):
            trans_type = TransactionType.DEBIT
            amount = -abs(amount) if amount > 0 else amount
        else:
            # Default based on sign
            if amount >= 0:
                trans_type = TransactionType.CREDIT
            else:
                trans_type = TransactionType.DEBIT

        # Build description
        desc_parts = [raw.activity]
        if raw.description:
            desc_parts.append(raw.description)
        if raw.quantity and raw.price:
            desc_parts.append(f"({raw.quantity} @ ${raw.price:.2f})")

        raw_text = f"{raw.date_str} {raw.activity} {raw.description}"
        if raw.quantity:
            raw_text += f" qty={raw.quantity}"
        if raw.price:
            raw_text += f" price={raw.price}"
        raw_text += f" amount={raw.amount}"

        return Transaction(
            date=trans_date,
            description=' '.join(desc_parts),
            amount=amount,
            balance=0.0,  # Investment statements don't have running balance per transaction
            transaction_type=trans_type,
            store=raw.activity,
            location="",
            raw_text=raw_text
        )

    def _detect_year_from_filename(self, filename: str) -> int:
        """Detect year from filename."""
        match = re.search(r'(\d{2})-(\d{4})\.pdf$', filename)
        if match:
            return int(match.group(2))
        match = re.search(r'20\d{2}', filename)
        if match:
            return int(match.group())
        return 2024  # Default

    def _detect_month_from_filename(self, filename: str) -> Optional[int]:
        """Detect month from filename."""
        # Format: Statement_54481201_06-2021.pdf (MM-YYYY)
        match = re.search(r'(\d{2})-\d{4}\.pdf$', filename)
        if match:
            return int(match.group(1))
        return None
