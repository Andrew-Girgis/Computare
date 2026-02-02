"""
Validation system for extracted transactions.
Ensures high accuracy through balance reconciliation and sanity checks.
"""

from typing import List, Tuple
from datetime import date

from .models import Transaction, ExtractionResult


class TransactionValidator:
    """Validates extracted transactions for accuracy."""

    def __init__(self, tolerance: float = 0.01):
        """
        Initialize validator.

        Args:
            tolerance: Acceptable difference for floating point comparisons (default $0.01)
        """
        self.tolerance = tolerance

    def validate(self, result: ExtractionResult) -> ExtractionResult:
        """
        Run all validations on extraction result.
        Updates the result's validation_passed and validation_errors fields.
        """
        errors = []

        # Run all validation checks
        balance_errors = self.validate_balance_continuity(result.transactions)
        errors.extend(balance_errors)

        date_errors = self.validate_date_sequence(result.transactions)
        errors.extend(date_errors)

        amount_errors = self.validate_amounts(result.transactions)
        errors.extend(amount_errors)

        duplicate_errors = self.detect_duplicates(result.transactions)
        errors.extend(duplicate_errors)

        # Validate against opening/closing balance if available
        if result.metadata.opening_balance and result.metadata.closing_balance:
            reconcile_errors = self.validate_balance_reconciliation(
                result.transactions,
                result.metadata.opening_balance,
                result.metadata.closing_balance
            )
            errors.extend(reconcile_errors)

        # Update result
        result.validation_errors = errors
        result.validation_passed = len(errors) == 0

        return result

    def validate_balance_continuity(self, transactions: List[Transaction]) -> List[str]:
        """
        Check that running balance is continuous across transactions.
        Each transaction's balance should equal previous balance + amount.
        """
        errors = []

        for i in range(1, len(transactions)):
            prev = transactions[i - 1]
            curr = transactions[i]

            expected_balance = prev.balance + curr.amount

            if abs(expected_balance - curr.balance) > self.tolerance:
                errors.append(
                    f"Balance discontinuity at index {i}: "
                    f"expected {expected_balance:.2f}, got {curr.balance:.2f} "
                    f"(transaction: {curr.date} {curr.description[:30]})"
                )

        return errors

    def validate_date_sequence(self, transactions: List[Transaction]) -> List[str]:
        """
        Check that transaction dates are in chronological order.
        Note: Some banks may have same-day transactions in any order.
        """
        errors = []

        for i in range(1, len(transactions)):
            prev_date = transactions[i - 1].date
            curr_date = transactions[i].date

            # Only flag if dates go backwards (same day is OK)
            if curr_date < prev_date:
                errors.append(
                    f"Date sequence error at index {i}: "
                    f"{curr_date} comes after {prev_date} "
                    f"(transaction: {transactions[i].description[:30]})"
                )

        return errors

    def validate_amounts(self, transactions: List[Transaction]) -> List[str]:
        """Check for suspicious amounts (zero, extremely large, etc.)."""
        errors = []

        for i, trans in enumerate(transactions):
            # Zero amount is suspicious
            if trans.amount == 0:
                errors.append(
                    f"Zero amount at index {i}: {trans.date} {trans.description[:30]}"
                )

            # Extremely large amounts (over $100k) - flag for review
            if abs(trans.amount) > 100000:
                errors.append(
                    f"Unusually large amount at index {i}: "
                    f"${trans.amount:,.2f} - {trans.date} {trans.description[:30]}"
                )

        return errors

    def detect_duplicates(self, transactions: List[Transaction]) -> List[str]:
        """
        Detect potential duplicate transactions.
        Same date, amount, and similar description = potential duplicate.
        """
        errors = []
        seen = {}

        for i, trans in enumerate(transactions):
            # Create a key based on date and amount
            key = (trans.date, trans.amount)

            if key in seen:
                prev_idx = seen[key]
                prev_trans = transactions[prev_idx]

                # Check if descriptions are similar
                if self._descriptions_similar(prev_trans.description, trans.description):
                    errors.append(
                        f"Potential duplicate at index {i} (matches index {prev_idx}): "
                        f"{trans.date} ${trans.amount:.2f} {trans.description[:30]}"
                    )
            else:
                seen[key] = i

        return errors

    def _descriptions_similar(self, desc1: str, desc2: str) -> bool:
        """Check if two descriptions are similar enough to be duplicates."""
        # Simple check: first 10 characters match
        return desc1[:10].upper() == desc2[:10].upper()

    def validate_balance_reconciliation(
        self,
        transactions: List[Transaction],
        opening_balance: float,
        closing_balance: float
    ) -> List[str]:
        """
        Validate that transactions reconcile with statement balances.
        opening_balance + sum(amounts) should equal closing_balance.
        """
        errors = []

        if not transactions:
            return errors

        total_amount = sum(t.amount for t in transactions)
        calculated_closing = opening_balance + total_amount

        if abs(calculated_closing - closing_balance) > self.tolerance:
            errors.append(
                f"Balance reconciliation failed: "
                f"Opening (${opening_balance:,.2f}) + Transactions (${total_amount:,.2f}) = "
                f"${calculated_closing:,.2f}, but closing balance is ${closing_balance:,.2f}. "
                f"Difference: ${abs(calculated_closing - closing_balance):,.2f}"
            )

        # Also check if last transaction balance matches closing
        if transactions:
            last_balance = transactions[-1].balance
            if abs(last_balance - closing_balance) > self.tolerance:
                errors.append(
                    f"Last transaction balance (${last_balance:,.2f}) "
                    f"doesn't match closing balance (${closing_balance:,.2f})"
                )

        return errors

    def get_summary(self, result: ExtractionResult) -> dict:
        """Generate a validation summary report."""
        transactions = result.transactions

        total_debits = sum(t.amount for t in transactions if t.amount < 0)
        total_credits = sum(t.amount for t in transactions if t.amount > 0)
        net_change = total_debits + total_credits

        return {
            "transaction_count": len(transactions),
            "total_debits": round(total_debits, 2),
            "total_credits": round(total_credits, 2),
            "net_change": round(net_change, 2),
            "date_range": {
                "start": transactions[0].date.isoformat() if transactions else None,
                "end": transactions[-1].date.isoformat() if transactions else None
            },
            "validation_passed": result.validation_passed,
            "error_count": len(result.validation_errors),
            "errors": result.validation_errors,
            "confidence_score": result.confidence_score,
            "extraction_method": result.extraction_method.value
        }
