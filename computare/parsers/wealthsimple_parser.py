"""
Wealthsimple CSV parsers.

Handles different Wealthsimple CSV formats:
- Investments (TFSA/Personal): trades, dividends, contributions
- Spending (Cash account): everyday transactions
- Credit Card: purchases and payments
- Activities Export: master export with all activity
"""

import csv
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from dataclasses import dataclass


@dataclass
class WealthsimpleTransaction:
    """Unified transaction representation for all Wealthsimple accounts."""
    date: date
    transaction_type: str  # BUY, SELL, CONT, DIV, etc.
    description: str
    amount: float
    balance: Optional[float]
    currency: str
    account_type: str  # investments, spending, credit_card, crypto
    symbol: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    raw_data: Optional[Dict[str, Any]] = None


class WealthsimpleInvestmentsParser:
    """
    Parser for Wealthsimple Investments CSV files.

    Format:
    date,transaction,description,amount,balance,currency
    "2024-10-18","CONT","Contribution...","1000.0","1000.33","CAD"
    """

    # Transaction types
    TRANSACTION_TYPES = {
        'CONT': 'Contribution',
        'BUY': 'Buy',
        'SELL': 'Sell',
        'DIV': 'Dividend',
        'NRT': 'Non-resident Tax',
        'WDR': 'Withdrawal',
        'DEP': 'Deposit',
        'FEE': 'Fee',
        'INT': 'Interest',
        'TFR': 'Transfer',
    }

    def parse(self, csv_path: str | Path) -> List[WealthsimpleTransaction]:
        """Parse a Wealthsimple Investments CSV file."""
        csv_path = Path(csv_path)
        transactions = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                trans = self._parse_row(row)
                if trans:
                    transactions.append(trans)

        return transactions

    def _parse_row(self, row: Dict[str, str]) -> Optional[WealthsimpleTransaction]:
        """Parse a single CSV row."""
        try:
            date_str = row.get('date', '').strip('"')
            trans_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            trans_type = row.get('transaction', '').strip('"')
            description = row.get('description', '').strip('"')
            amount = float(row.get('amount', '0').strip('"'))

            balance_str = row.get('balance', '').strip('"')
            balance = float(balance_str) if balance_str else None

            currency = row.get('currency', 'CAD').strip('"')

            # Extract symbol from description
            symbol = self._extract_symbol(description)
            quantity, unit_price = self._extract_trade_details(description)

            return WealthsimpleTransaction(
                date=trans_date,
                transaction_type=trans_type,
                description=description,
                amount=amount,
                balance=balance,
                currency=currency,
                account_type='investments',
                symbol=symbol,
                quantity=quantity,
                unit_price=unit_price,
                raw_data=dict(row)
            )
        except Exception as e:
            print(f"Error parsing row: {row}, error: {e}")
            return None

    def _extract_symbol(self, description: str) -> Optional[str]:
        """Extract stock symbol from description."""
        # Format: "NVDA - Nvidia Corp: Bought 5.0000 shares"
        match = re.match(r'^([A-Z0-9]+)\s*-', description)
        if match:
            return match.group(1)
        return None

    def _extract_trade_details(self, description: str) -> tuple:
        """Extract quantity and price from trade description."""
        # Format: "Bought 5.0000 shares (executed at 2024-10-21)"
        qty_match = re.search(r'(?:Bought|Sold)\s+([\d.]+)\s+shares', description)
        quantity = float(qty_match.group(1)) if qty_match else None

        # Price is not in the description, would need to calculate from amount/quantity
        return quantity, None


class WealthsimpleSpendingParser:
    """
    Parser for Wealthsimple Spending (Cash Account) CSV files.

    Format:
    date,transaction,description,amount,balance,currency
    Same as investments, but different transaction types
    """

    def parse(self, csv_path: str | Path) -> List[WealthsimpleTransaction]:
        """Parse a Wealthsimple Spending CSV file."""
        csv_path = Path(csv_path)
        transactions = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                trans = self._parse_row(row)
                if trans:
                    transactions.append(trans)

        return transactions

    def _parse_row(self, row: Dict[str, str]) -> Optional[WealthsimpleTransaction]:
        """Parse a single CSV row."""
        try:
            date_str = row.get('date', '').strip('"')
            trans_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            trans_type = row.get('transaction', '').strip('"')
            description = row.get('description', '').strip('"')
            amount = float(row.get('amount', '0').strip('"'))

            balance_str = row.get('balance', '').strip('"')
            balance = float(balance_str) if balance_str else None

            currency = row.get('currency', 'CAD').strip('"')

            return WealthsimpleTransaction(
                date=trans_date,
                transaction_type=trans_type,
                description=description,
                amount=amount,
                balance=balance,
                currency=currency,
                account_type='spending',
                raw_data=dict(row)
            )
        except Exception as e:
            print(f"Error parsing row: {row}, error: {e}")
            return None


class WealthsimpleCreditCardParser:
    """
    Parser for Wealthsimple Credit Card CSV files.

    Format:
    transaction_date,post_date,type,details,amount,currency
    "2025-11-20","2025-11-21","Purchase","ROGERS ******2820","82.31","CAD"
    """

    def parse(self, csv_path: str | Path) -> List[WealthsimpleTransaction]:
        """Parse a Wealthsimple Credit Card CSV file."""
        csv_path = Path(csv_path)
        transactions = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                trans = self._parse_row(row)
                if trans:
                    transactions.append(trans)

        return transactions

    def _parse_row(self, row: Dict[str, str]) -> Optional[WealthsimpleTransaction]:
        """Parse a single CSV row."""
        try:
            date_str = row.get('transaction_date', '').strip('"')
            trans_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            trans_type = row.get('type', '').strip('"')
            description = row.get('details', '').strip('"')
            amount = float(row.get('amount', '0').strip('"'))
            currency = row.get('currency', 'CAD').strip('"')

            # Credit card: purchases are positive in CSV but should be negative (money out)
            # Payments are typically labeled differently
            if trans_type == 'Purchase':
                amount = -abs(amount)
            elif trans_type == 'Payment':
                amount = abs(amount)

            return WealthsimpleTransaction(
                date=trans_date,
                transaction_type=trans_type,
                description=description,
                amount=amount,
                balance=None,  # Credit card CSVs don't have running balance
                currency=currency,
                account_type='credit_card',
                raw_data=dict(row)
            )
        except Exception as e:
            print(f"Error parsing row: {row}, error: {e}")
            return None


class WealthsimpleActivitiesParser:
    """
    Parser for Wealthsimple Activities Export CSV.

    Format:
    transaction_date,settlement_date,account_id,account_type,activity_type,
    activity_sub_type,direction,symbol,name,currency,quantity,unit_price,
    commission,net_cash_amount
    """

    def parse(self, csv_path: str | Path) -> List[WealthsimpleTransaction]:
        """Parse a Wealthsimple Activities Export CSV file."""
        csv_path = Path(csv_path)
        transactions = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                trans = self._parse_row(row)
                if trans:
                    transactions.append(trans)

        return transactions

    def _parse_row(self, row: Dict[str, str]) -> Optional[WealthsimpleTransaction]:
        """Parse a single CSV row."""
        try:
            date_str = row.get('transaction_date', '').strip()

            # Skip header/footer rows like "As of 2026-01-18 13:19 GMT-05:00"
            if not date_str or 'As of' in date_str or len(date_str) != 10:
                return None

            trans_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            account_type = row.get('account_type', '').strip().lower()
            activity_type = row.get('activity_type', '').strip()
            activity_sub_type = row.get('activity_sub_type', '').strip()
            direction = row.get('direction', '').strip()

            symbol = row.get('symbol', '').strip()
            name = row.get('name', '').strip()
            currency = row.get('currency', 'CAD').strip()

            quantity_str = row.get('quantity', '').strip()
            quantity = float(quantity_str) if quantity_str else None

            unit_price_str = row.get('unit_price', '').strip()
            unit_price = float(unit_price_str) if unit_price_str else None

            net_cash_str = row.get('net_cash_amount', '').strip()
            amount = float(net_cash_str) if net_cash_str else 0.0

            # Build description
            if symbol and name:
                description = f"{symbol} - {name}"
                if activity_sub_type:
                    description += f": {activity_sub_type}"
                if quantity:
                    description += f" ({quantity} @ ${unit_price:.2f})" if unit_price else f" ({quantity})"
            else:
                description = f"{activity_type} {activity_sub_type}".strip()

            # Combine activity type and sub type
            trans_type = f"{activity_type}_{activity_sub_type}" if activity_sub_type else activity_type

            return WealthsimpleTransaction(
                date=trans_date,
                transaction_type=trans_type,
                description=description,
                amount=amount,
                balance=None,
                currency=currency,
                account_type=account_type,
                symbol=symbol if symbol else None,
                quantity=quantity,
                unit_price=unit_price,
                raw_data=dict(row)
            )
        except Exception as e:
            print(f"Error parsing row: {row}, error: {e}")
            return None


def parse_all_wealthsimple(
    wealthsimple_dir: str | Path,
    use_subfolder_only: bool = True
) -> Dict[str, List[WealthsimpleTransaction]]:
    """
    Parse all Wealthsimple CSV files in a directory.

    Args:
        wealthsimple_dir: Path to Wealthsimple folder
        use_subfolder_only: If True, prefer organized subfolder to avoid duplicates

    Returns a dictionary with keys: investments, spending, credit_card, activities, crypto
    """
    wealthsimple_dir = Path(wealthsimple_dir)

    results = {
        'investments': [],
        'spending': [],
        'credit_card': [],
        'activities': [],
        'crypto': [],
    }

    investments_parser = WealthsimpleInvestmentsParser()
    spending_parser = WealthsimpleSpendingParser()
    credit_card_parser = WealthsimpleCreditCardParser()
    activities_parser = WealthsimpleActivitiesParser()

    # Determine which files to process
    if use_subfolder_only:
        # Use the organized subfolder for monthly statements
        subfolder = wealthsimple_dir / 'Wealthsimple Monthly Statements 2021-2026'
        csv_files = list(subfolder.glob('*.csv')) if subfolder.exists() else []

        # Also add the activities export from root (it's unique)
        for f in wealthsimple_dir.glob('*.csv'):
            if 'activities export' in f.name.lower():
                csv_files.append(f)
    else:
        csv_files = list(wealthsimple_dir.rglob('*.csv'))

    # Process CSVs
    for csv_file in csv_files:
        filename = csv_file.name.lower()
        original_name = csv_file.name

        if 'activities export' in filename:
            transactions = activities_parser.parse(csv_file)
            results['activities'].extend(transactions)
        elif 'credit-card' in filename:
            transactions = credit_card_parser.parse(csv_file)
            results['credit_card'].extend(transactions)
        elif '🤖' in original_name or 'crypto' in filename:
            # Use investments parser for crypto (same format)
            transactions = investments_parser.parse(csv_file)
            for t in transactions:
                t.account_type = 'crypto'
            results['crypto'].extend(transactions)
        elif '💳' in original_name or 'spending' in filename:
            transactions = spending_parser.parse(csv_file)
            results['spending'].extend(transactions)
        elif '📈' in original_name or 'investment' in filename:
            transactions = investments_parser.parse(csv_file)
            results['investments'].extend(transactions)

    # Sort each list by date
    for key in results:
        results[key].sort(key=lambda t: t.date)

    return results
