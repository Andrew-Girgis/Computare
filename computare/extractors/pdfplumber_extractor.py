"""
PDF extraction using pdfplumber - primary extraction method.
Fast, free, and accurate for text-based PDFs.

Uses positional word extraction to properly handle multi-column layouts
like Scotiabank statements with separate Withdrawn/Deposited columns.
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
class RawTransaction:
    """Intermediate representation before final Transaction object."""
    date_str: str
    description: str
    withdrawn: Optional[float]
    deposited: Optional[float]
    balance: float
    store: str
    location: str
    row_top: float  # Y position for debugging


class PdfPlumberExtractor(BaseExtractor):
    """
    Extracts transactions from bank statements using pdfplumber.
    Uses positional extraction to handle multi-column layouts.
    """

    MONTHS = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
        'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
        'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }

    # Date pattern: Mar18, Apr 5, etc.
    DATE_PATTERN = re.compile(r'^([A-Z][a-z]{2})(\d{1,2})$')

    # Scotiabank column boundaries (approximate x positions)
    # These define the columns: Date | Description | Withdrawn | Deposited | Balance
    # Based on actual PDF analysis:
    # - Withdrawn amounts appear around x=271-290 (large amounts start around 271)
    # - Deposited amounts appear around x=336-350
    # - Balance appears around x=400-408
    SCOTIABANK_COLUMNS = {
        'date_max': 110,        # Date column ends around x=110
        'desc_max': 265,        # Description ends before withdrawn amounts
        'withdrawn_min': 265,   # Withdrawn column starts (amounts at ~271-290)
        'withdrawn_max': 320,   # Withdrawn column ends (gap before deposits at ~336)
        'deposited_min': 320,   # Deposited column starts (amounts at ~336-353)
        'deposited_max': 395,   # Deposited column ends
        'balance_min': 395,     # Balance column starts (amounts at ~401-418)
    }

    def can_handle(self, pdf_path: str | Path) -> bool:
        """Check if PDF is text-based and can be handled."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) == 0:
                    return False
                text = pdf.pages[0].extract_text()
                return text is not None and len(text) > 100
        except Exception:
            return False

    def extract(self, pdf_path: str | Path, year: Optional[int] = None) -> ExtractionResult:
        """Extract transactions from PDF using positional word extraction."""
        pdf_path = Path(pdf_path)
        year = year or self._detect_year_from_filename(pdf_path.name) or DEFAULT_YEAR
        statement_month = self._detect_month_from_filename(pdf_path.name)

        all_transactions: List[Transaction] = []
        raw_transactions: List[RawTransaction] = []
        issues = 0

        metadata = StatementMetadata(bank="unknown")

        with pdfplumber.open(pdf_path) as pdf:
            # Extract first page for metadata (Scotiabank has summary on first page)
            if pdf.pages:
                first_page_text = pdf.pages[0].extract_text() or ""
                bank = self.detect_bank(first_page_text)
                if bank:
                    metadata.bank = bank
                metadata.opening_balance = self._extract_opening_balance(first_page_text)
                # Scotiabank puts closing balance in summary on first page
                metadata.closing_balance = self._extract_closing_balance(first_page_text)

            # Process each page using positional extraction
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue

                # Check if this page has transactions
                if "Balance($)" not in text:
                    continue

                # Extract transactions using word positions
                page_transactions = self._extract_transactions_positional(page, year)
                raw_transactions.extend(page_transactions)

            # If closing balance not found on first page, try last page
            if metadata.closing_balance is None and pdf.pages:
                last_page_text = pdf.pages[-1].extract_text() or ""
                metadata.closing_balance = self._extract_closing_balance(last_page_text)

        # Convert raw transactions to Transaction objects
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

    def _extract_transactions_positional(self, page, year: int) -> List[RawTransaction]:
        """
        Extract transactions using word positions to handle columns properly.
        """
        transactions = []

        # Get all words with their positions
        words = page.extract_words()
        if not words:
            return transactions

        # Find the transaction section boundaries
        # Look for "Balance($)" header which appears in the right column (x > 350)
        balance_marker_top = None
        for word in words:
            # The column header "Balance($)" is in the balance column (right side)
            if "Balance($)" in word['text'] or (word['text'] == "Balance($)"):
                balance_marker_top = word['top']
                break
            # Also check for just "Balance" but only if it's in the header position (x > 350)
            if word['text'] == "Balance" and word['x0'] > 350:
                balance_marker_top = word['top']
                break

        if balance_marker_top is None:
            return transactions

        # Find end markers
        end_top = float('inf')
        for word in words:
            text = word['text'].lower()
            if 'continuedonnextpage' in text or 'closingbalance' in text:
                if word['top'] > balance_marker_top:
                    end_top = word['top']
                    break
            # Also check for "Closing" followed by "Balance"
            if word['text'] == 'Closing' and word['x0'] < 150:
                if word['top'] > balance_marker_top:
                    end_top = word['top']
                    break

        # Group words by row (similar Y positions)
        rows = self._group_words_by_row(words, balance_marker_top, end_top)

        # Process each row
        current_transaction = None
        continuation_row = False

        for row_top, row_words in sorted(rows.items()):
            # Check if this row starts with a date
            date_word = self._find_date_in_row(row_words)

            if date_word:
                # This is a new transaction row
                if current_transaction:
                    transactions.append(current_transaction)

                current_transaction = self._parse_transaction_row(row_words, row_top)
                continuation_row = False
            else:
                # This is a continuation row (store name, etc.)
                if current_transaction and not continuation_row:
                    store_info = self._extract_store_from_row(row_words)
                    if store_info:
                        current_transaction.store = store_info[0]
                        current_transaction.location = store_info[1]
                    continuation_row = True

        # Don't forget the last transaction
        if current_transaction:
            transactions.append(current_transaction)

        return transactions

    def _group_words_by_row(self, words: List[dict], min_top: float, max_top: float) -> Dict[float, List[dict]]:
        """Group words into rows based on Y position."""
        rows = {}
        tolerance = 3  # Words within 3 points are on the same row

        for word in words:
            # Skip words outside transaction section
            if word['top'] <= min_top or word['top'] >= max_top:
                continue

            # Skip words in the left margin (document codes, not transaction data)
            if word['x0'] < 50:
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

    def _find_date_in_row(self, row_words: List[dict]) -> Optional[dict]:
        """Find a date word at the start of a row."""
        if not row_words:
            return None

        first_word = row_words[0]
        # Check if it matches date pattern (e.g., "Mar18", "Apr5")
        if self.DATE_PATTERN.match(first_word['text']):
            return first_word

        return None

    def _parse_transaction_row(self, row_words: List[dict], row_top: float) -> Optional[RawTransaction]:
        """Parse a row of words into a RawTransaction."""
        if not row_words:
            return None

        cols = self.SCOTIABANK_COLUMNS

        date_str = ""
        description_parts = []
        withdrawn = None
        deposited = None
        balance = None

        for word in row_words:
            x = word['x0']
            text = word['text']

            if x < cols['date_max']:
                # Date column
                if self.DATE_PATTERN.match(text):
                    date_str = text
            elif x < cols['desc_max']:
                # Description column
                description_parts.append(text)
            elif x < cols['withdrawn_max']:
                # Withdrawn column
                amount = self._parse_amount(text)
                if amount is not None:
                    withdrawn = amount
            elif x < cols['deposited_max']:
                # Deposited column
                amount = self._parse_amount(text)
                if amount is not None:
                    deposited = amount
            else:
                # Balance column (or beyond)
                amount = self._parse_amount(text)
                if amount is not None:
                    balance = amount

        if not date_str or balance is None:
            return None

        return RawTransaction(
            date_str=date_str,
            description=' '.join(description_parts),
            withdrawn=withdrawn,
            deposited=deposited,
            balance=balance,
            store="",
            location="",
            row_top=row_top
        )

    def _extract_store_from_row(self, row_words: List[dict]) -> Optional[Tuple[str, str]]:
        """Extract store name and location from continuation row."""
        if not row_words:
            return None

        # Join all text in the row
        text = ' '.join(w['text'] for w in row_words)

        # Check for location code at end
        location = ""
        store = text

        # Common location patterns: ONCA, BCCA, ABCA, SE, US, etc.
        location_match = re.search(r'\s+([A-Z]{2,4})$', text)
        if location_match:
            location = location_match.group(1)
            store = text[:location_match.start()].strip()

        # Also check for embedded location codes
        if not location:
            embedded_match = re.search(r'([A-Z]{2}(?:CA|US)?)(?:\s|$)', text)
            if embedded_match:
                location = embedded_match.group(1)

        return (store, location) if store else None

    def _parse_amount(self, text: str) -> Optional[float]:
        """Parse an amount string to float."""
        if not text:
            return None

        # Remove common non-numeric characters
        cleaned = text.replace(',', '').replace('$', '').strip()

        # Check if it's a valid number
        try:
            return float(cleaned)
        except ValueError:
            return None

    def _convert_to_transaction(self, raw: RawTransaction, year: int, statement_month: Optional[int] = None) -> Optional[Transaction]:
        """Convert RawTransaction to Transaction object."""
        # Skip "OpeningBalance" entries - they're just markers, not transactions
        if 'openingbalance' in raw.description.lower().replace(' ', ''):
            return None

        # Parse date
        date_match = self.DATE_PATTERN.match(raw.date_str)
        if not date_match:
            return None

        month_abbr = date_match.group(1)
        day = int(date_match.group(2))
        month = self.MONTHS.get(month_abbr)
        if not month:
            return None

        # Handle year boundary: if statement is January but transaction is in Nov/Dec,
        # the transaction is from the previous year
        actual_year = year
        if statement_month is not None:
            if statement_month <= 2 and month >= 11:  # Jan/Feb statement with Nov/Dec transaction
                actual_year = year - 1
            elif statement_month >= 11 and month <= 2:  # Nov/Dec statement with Jan/Feb transaction
                actual_year = year + 1

        try:
            trans_date = date(actual_year, month, day)
        except ValueError:
            return None

        # Determine amount and type
        if raw.withdrawn is not None:
            amount = -raw.withdrawn
            trans_type = TransactionType.DEBIT
        elif raw.deposited is not None:
            amount = raw.deposited
            trans_type = TransactionType.CREDIT
        else:
            # Fallback: try to extract amount from description text
            trans_type = self._determine_transaction_type(raw.description)
            amount = self._extract_amount_from_description(raw.description)
            if amount is not None:
                # Apply sign based on transaction type
                if trans_type == TransactionType.DEBIT:
                    amount = -abs(amount)
                else:
                    amount = abs(amount)
            else:
                amount = 0  # We don't have an amount, this is an error case

        # Build raw text for debugging
        raw_text = f"{raw.date_str} {raw.description}"
        if raw.withdrawn:
            raw_text += f" W:{raw.withdrawn}"
        if raw.deposited:
            raw_text += f" D:{raw.deposited}"
        raw_text += f" B:{raw.balance}"
        if raw.store:
            raw_text += f" {raw.store}"
        if raw.location:
            raw_text += f" {raw.location}"

        return Transaction(
            date=trans_date,
            description=raw.description,
            amount=amount,
            balance=raw.balance,
            transaction_type=trans_type,
            store=raw.store,
            location=raw.location,
            raw_text=raw_text
        )

    def _determine_transaction_type(self, description: str) -> TransactionType:
        """Determine if transaction is debit or credit based on description."""
        description_upper = description.upper()

        credit_keywords = [
            'DEPOSIT', 'CREDIT', 'TRANSFER IN', 'PAYROLL', 'SALARY',
            'REFUND', 'REBATE', 'INTEREST', 'TAXREFUND'
        ]

        debit_keywords = [
            'PURCHASE', 'WITHDRAWAL', 'PAYMENT', 'DEBIT', 'POS',
            'INTERAC', 'ATM', 'FEE', 'CHARGE', 'PAY TO'
        ]

        for keyword in credit_keywords:
            if keyword in description_upper:
                return TransactionType.CREDIT

        for keyword in debit_keywords:
            if keyword in description_upper:
                return TransactionType.DEBIT

        return TransactionType.UNKNOWN

    def _extract_amount_from_description(self, description: str) -> Optional[float]:
        """Extract amount from description text when column extraction fails.

        Handles cases like:
        - 'MB-Billpayment 128.24'
        - 'Withdrawal 300.00'
        - 'Pointofsalepurchase 114.08'
        """
        # Look for amount pattern at the end of description
        # Match patterns like: 123.45, 1,234.56, 1234.56
        amount_pattern = re.search(r'[\s]+([\d,]+\.\d{2})$', description)
        if amount_pattern:
            amount_str = amount_pattern.group(1).replace(',', '')
            try:
                return float(amount_str)
            except ValueError:
                pass

        return None

    def _detect_year_from_filename(self, filename: str) -> Optional[int]:
        """Try to detect year from filename like 'April 2024 e-statement.pdf'."""
        match = re.search(r'20\d{2}', filename)
        if match:
            return int(match.group())
        return None

    def _detect_month_from_filename(self, filename: str) -> Optional[int]:
        """Try to detect month from filename like 'April 2024 e-statement.pdf'."""
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

    def _extract_opening_balance(self, text: str) -> Optional[float]:
        """Try to extract opening balance from page."""
        patterns = [
            # Scotiabank format: "OpeningBalanceonOctober18,2021 $690.99"
            r'OpeningBalance(?:on[A-Za-z]+\d+,\d{4})?\s*\$?([\d,]+\.\d{2})',
            r'Opening\s*Balance[:\s]*\$?([\d,]+\.\d{2})',
            r'Previous\s*Balance[:\s]*\$?([\d,]+\.\d{2})',
            r'Balance\s*Forward[:\s]*\$?([\d,]+\.\d{2})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', ''))

        return None

    def _extract_closing_balance(self, text: str) -> Optional[float]:
        """Try to extract closing balance from page."""
        patterns = [
            # Scotiabank format: "ClosingBalanceonNovember17,2021 $147.41"
            r'ClosingBalance(?:on[A-Za-z]+\d+,\d{4})?\s*\$?([\d,]+\.\d{2})',
            r'Closing\s*Balance[:\s]*\$?([\d,]+\.\d{2})',
            r'Ending\s*Balance[:\s]*\$?([\d,]+\.\d{2})',
            r'New\s*Balance[:\s]*\$?([\d,]+\.\d{2})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', ''))

        return None
