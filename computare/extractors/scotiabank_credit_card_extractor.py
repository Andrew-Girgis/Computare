"""
Scotiabank Credit Card PDF extractor.

Separate from chequing account extractor due to different format:
- Has REF# column
- Two date columns (Trans date, Post date)
- Single AMOUNT column (no separate withdrawn/deposited)
- Credits shown with trailing minus sign (e.g., "366.01-")
- No running balance column
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from datetime import date
from dataclasses import dataclass

import pdfplumber

from .base import BaseExtractor
from ..models import (
    Transaction, TransactionType, ExtractionResult,
    StatementMetadata, ExtractionMethod
)
from ..config import DEFAULT_YEAR


@dataclass
class CreditCardTransaction:
    """Intermediate representation for credit card transactions."""
    ref_num: str
    trans_date_str: str
    post_date_str: str
    description: str
    amount: float
    is_credit: bool  # True if this is a payment/refund (negative on statement)
    row_top: float


class ScotiabankCreditCardExtractor(BaseExtractor):
    """
    Extracts transactions from Scotiabank Credit Card statements.
    Uses positional extraction to handle the specific column layout.
    """

    MONTHS = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
        'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
        'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }

    # Date pattern: Mar 1, Apr 16, etc.
    DATE_PATTERN = re.compile(r'^([A-Z][a-z]{2})$')
    DAY_PATTERN = re.compile(r'^(\d{1,2})$')

    # Scotiabank Credit Card column boundaries (based on PDF analysis)
    # REF# | TRANS DATE | POST DATE | DETAILS | AMOUNT($)
    # Actual positions from PDF:
    #   REF# at x=82, dates at x=103-145, details start at x=159, amount at x=338-365
    #   (Beyond x=370 is SCENE points column which we ignore)
    COLUMNS = {
        'ref_max': 100,          # REF# column ends
        'trans_date_max': 128,   # Trans date column ends (Mar at 103, day at 117)
        'post_date_max': 158,    # Post date column ends (Mar at 131, day at 145)
        'details_max': 335,      # Details column ends (amounts start at ~338)
        'amount_min': 335,       # Amount column starts
        'amount_max': 370,       # Amount column ends (excludes SCENE points at x~567)
    }

    def can_handle(self, pdf_path: str | Path) -> bool:
        """Check if this is a Scotiabank Credit Card statement."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) == 0:
                    return False
                text = pdf.pages[0].extract_text() or ""

                # Check for credit card specific markers
                is_credit_card = (
                    "VISA" in text.upper() or
                    "Scene+" in text or
                    "SCENE VISA" in text
                )
                is_scotiabank = "scotiabank" in text.lower() or "scotia" in text.lower()
                has_ref_column = "REF.#" in text

                return is_credit_card and is_scotiabank and has_ref_column
        except Exception:
            return False

    def extract(self, pdf_path: str | Path, year: Optional[int] = None) -> ExtractionResult:
        """Extract transactions from Scotiabank Credit Card PDF."""
        pdf_path = Path(pdf_path)
        year = year or self._detect_year_from_filename(pdf_path.name) or DEFAULT_YEAR
        statement_month = self._detect_month_from_filename(pdf_path.name)

        all_transactions: List[Transaction] = []
        raw_transactions: List[CreditCardTransaction] = []
        issues = 0

        metadata = StatementMetadata(bank="Scotiabank Credit Card")

        with pdfplumber.open(pdf_path) as pdf:
            # Extract metadata from first page
            if pdf.pages:
                first_page_text = pdf.pages[0].extract_text() or ""
                metadata.opening_balance = self._extract_previous_balance(first_page_text)
                metadata.closing_balance = self._extract_new_balance(first_page_text)

                # Extract statement period
                period_match = re.search(
                    r'Statement\s*Period\s*([A-Z][a-z]{2}\s*\d{1,2},?\s*\d{4})\s*-\s*([A-Z][a-z]{2}\s*\d{1,2},?\s*\d{4})',
                    first_page_text, re.IGNORECASE
                )
                if period_match:
                    metadata.statement_period = f"{period_match.group(1)} - {period_match.group(2)}"

            # Process each page
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""

                # Skip pages without transactions
                if "REF.#" not in text and "TRANS." not in text:
                    # Check if this is a continuation page with transactions
                    words = page.extract_words()
                    has_ref_nums = any(
                        w['text'].isdigit() and len(w['text']) == 3 and w['x0'] < 100
                        for w in words
                    )
                    if not has_ref_nums:
                        continue

                # Extract transactions from this page
                page_transactions = self._extract_transactions_from_page(page, year)
                raw_transactions.extend(page_transactions)

        # Convert to Transaction objects
        for raw in raw_transactions:
            trans = self._convert_to_transaction(raw, year, statement_month)
            if trans:
                all_transactions.append(trans)
            else:
                issues += 1

        # Calculate confidence
        total = len(raw_transactions) + issues
        confidence = (len(all_transactions) / max(total, 1)) if total > 0 else 0.0

        return ExtractionResult(
            transactions=all_transactions,
            metadata=metadata,
            extraction_method=ExtractionMethod.PDFPLUMBER,
            confidence_score=confidence,
            source_file=str(pdf_path)
        )

    def _extract_transactions_from_page(self, page, year: int) -> List[CreditCardTransaction]:
        """Extract transactions from a single page using positional extraction."""
        transactions = []
        words = page.extract_words()

        if not words:
            return transactions

        # Find transaction section boundaries
        # Look for "REF.#" or "TRANS." header
        header_top = None
        for w in words:
            if w['text'] in ['REF.#', 'TRANS.']:
                header_top = w['top']
                break

        if header_top is None:
            # Try to find transactions anyway by looking for ref numbers
            header_top = 0

        # Find the LAST "Interest charges" or "Continuedon" marker as end
        # (there may be multiple SUB-TOTAL markers for different card sections)
        end_top = float('inf')
        for w in words:
            text_lower = w['text'].lower()
            # Only use definitive end markers, not mid-page SUB-TOTALs
            if 'interestcharges' in text_lower.replace(' ', '') or 'continuedon' in text_lower:
                if w['top'] > header_top + 20:
                    end_top = min(end_top, w['top'])

        # If no definitive end marker, look for "Interest charges" as two words
        if end_top == float('inf'):
            for i, w in enumerate(words):
                if w['text'] == 'Interest' and w['x0'] < 150:  # Left side of page
                    # Check if next word on same line is "charges"
                    for w2 in words:
                        if abs(w2['top'] - w['top']) < 3 and w2['text'] == 'charges':
                            if w['top'] > header_top + 20:
                                end_top = w['top']
                                break

        # Group words by row - include ALL rows that have ref numbers
        # regardless of SUB-TOTAL markers
        rows = self._group_words_by_row(words, header_top + 10, end_top)

        # Process each row looking for transactions
        for row_top, row_words in sorted(rows.items()):
            transaction = self._parse_transaction_row(row_words, row_top)
            if transaction:
                transactions.append(transaction)

        return transactions

    def _group_words_by_row(self, words: List[dict], min_top: float, max_top: float) -> Dict[float, List[dict]]:
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

    def _parse_transaction_row(self, row_words: List[dict], row_top: float) -> Optional[CreditCardTransaction]:
        """Parse a row of words into a CreditCardTransaction."""
        if not row_words:
            return None

        cols = self.COLUMNS

        ref_num = ""
        trans_month = ""
        trans_day = ""
        post_month = ""
        post_day = ""
        description_parts = []
        amount = None
        is_credit = False

        for word in row_words:
            x = word['x0']
            text = word['text']

            if x < cols['ref_max']:
                # REF# column - look for 3-digit number
                if text.isdigit() and len(text) == 3:
                    ref_num = text
            elif x < cols['trans_date_max']:
                # Trans date column
                if self.DATE_PATTERN.match(text):
                    trans_month = text
                elif self.DAY_PATTERN.match(text):
                    trans_day = text
            elif x < cols['post_date_max']:
                # Post date column
                if self.DATE_PATTERN.match(text):
                    post_month = text
                elif self.DAY_PATTERN.match(text):
                    post_day = text
            elif x < cols['details_max']:
                # Details column
                description_parts.append(text)
            elif x <= cols['amount_max']:
                # Amount column (ignore anything beyond amount_max like SCENE points)
                parsed_amount, credit = self._parse_amount(text)
                if parsed_amount is not None:
                    amount = parsed_amount
                    is_credit = credit

        # Must have ref number and amount to be a valid transaction
        if not ref_num or amount is None:
            return None

        # Build date strings
        trans_date_str = f"{trans_month}{trans_day}" if trans_month and trans_day else ""
        post_date_str = f"{post_month}{post_day}" if post_month and post_day else ""

        return CreditCardTransaction(
            ref_num=ref_num,
            trans_date_str=trans_date_str,
            post_date_str=post_date_str,
            description=' '.join(description_parts),
            amount=amount,
            is_credit=is_credit,
            row_top=row_top
        )

    def _parse_amount(self, text: str) -> Tuple[Optional[float], bool]:
        """
        Parse amount string, detecting if it's a credit.
        Credits are shown with trailing minus: "366.01-"
        Returns (amount, is_credit)
        """
        if not text:
            return None, False

        text = text.strip()
        is_credit = False

        # Check for trailing minus (credit indicator)
        if text.endswith('-'):
            is_credit = True
            text = text[:-1]

        # Check for leading minus
        if text.startswith('-'):
            is_credit = True
            text = text[1:]

        # Remove common formatting
        cleaned = text.replace(',', '').replace('$', '').strip()

        try:
            return float(cleaned), is_credit
        except ValueError:
            return None, False

    def _convert_to_transaction(
        self,
        raw: CreditCardTransaction,
        year: int,
        statement_month: Optional[int] = None
    ) -> Optional[Transaction]:
        """Convert CreditCardTransaction to Transaction object."""

        # Parse transaction date (use trans_date, fall back to post_date)
        date_str = raw.trans_date_str or raw.post_date_str
        if not date_str or len(date_str) < 4:
            return None

        month_abbr = date_str[:3]
        day_str = date_str[3:]

        month = self.MONTHS.get(month_abbr)
        if not month:
            return None

        try:
            day = int(day_str)
        except ValueError:
            return None

        # Handle year boundary
        actual_year = year
        if statement_month is not None:
            if statement_month <= 2 and month >= 11:
                actual_year = year - 1
            elif statement_month >= 11 and month <= 2:
                actual_year = year + 1

        try:
            trans_date = date(actual_year, month, day)
        except ValueError:
            return None

        # Determine amount and type
        # For credit cards: purchases are debits (positive amount on statement)
        # Payments/refunds are credits (shown with minus on statement)
        if raw.is_credit:
            amount = raw.amount  # Payment/refund - positive in our system
            trans_type = TransactionType.CREDIT
        else:
            amount = -raw.amount  # Purchase - negative in our system
            trans_type = TransactionType.DEBIT

        # Build raw text for debugging
        raw_text = f"REF:{raw.ref_num} {raw.trans_date_str}/{raw.post_date_str} {raw.description} ${raw.amount}"
        if raw.is_credit:
            raw_text += " (CR)"

        return Transaction(
            date=trans_date,
            description=raw.description,
            amount=amount,
            balance=0.0,  # Credit cards don't have running balance per transaction
            transaction_type=trans_type,
            store=raw.description,  # Use description as store for now
            location="",
            raw_text=raw_text
        )

    def _extract_previous_balance(self, text: str) -> Optional[float]:
        """Extract previous balance from statement."""
        patterns = [
            r'Previous\s*balance[,\s]*[A-Z][a-z]{2}\s*\d{1,2}/\d{2}\s*\$?([\d,]+\.\d{2})',
            r'Previous\s*balance[:\s]*\$?([\d,]+\.\d{2})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', ''))
        return None

    def _extract_new_balance(self, text: str) -> Optional[float]:
        """Extract new balance from statement."""
        # Note: PDF may contain special chars like \x87 between words
        patterns = [
            r'New\s*[Bb]alance.?\s*=?\s*\$?([\d,]+\.\d{2})',
            r'Account\s*[Bb]alance.?\s*=?\s*\$?([\d,]+\.\d{2})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', ''))
        return None

    def _detect_year_from_filename(self, filename: str) -> Optional[int]:
        """Detect year from filename."""
        match = re.search(r'20\d{2}', filename)
        if match:
            return int(match.group())
        return None

    def _detect_month_from_filename(self, filename: str) -> Optional[int]:
        """Detect month from filename."""
        month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        filename_lower = filename.lower()
        for month_name, month_num in month_names.items():
            if month_name in filename_lower:
                return month_num
        return None
