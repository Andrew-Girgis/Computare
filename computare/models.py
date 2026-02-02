"""
Data models for Computare transaction extraction.
Using dataclasses for simplicity and type safety.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class TransactionType(Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    UNKNOWN = "unknown"


class ExtractionMethod(Enum):
    PDFPLUMBER = "pdfplumber"
    CLAUDE_AI = "claude_ai"
    MANUAL = "manual"


@dataclass
class Transaction:
    """Represents a single bank transaction."""
    date: date
    description: str
    amount: float  # Negative for debits, positive for credits
    balance: float
    transaction_type: TransactionType = TransactionType.UNKNOWN
    store: str = ""
    location: str = ""
    category: Optional[str] = None
    raw_text: str = ""  # Original text for debugging

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "date": self.date.isoformat() if isinstance(self.date, date) else self.date,
            "description": self.description,
            "amount": self.amount,
            "balance": self.balance,
            "transaction_type": self.transaction_type.value,
            "store": self.store,
            "location": self.location,
            "category": self.category,
            "raw_text": self.raw_text
        }


@dataclass
class StatementMetadata:
    """Metadata about the bank statement."""
    bank: str
    account_type: str = ""
    account_number_masked: str = ""
    statement_period_start: Optional[date] = None
    statement_period_end: Optional[date] = None
    opening_balance: Optional[float] = None
    closing_balance: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "bank": self.bank,
            "account_type": self.account_type,
            "account_number_masked": self.account_number_masked,
            "statement_period_start": self.statement_period_start.isoformat() if self.statement_period_start else None,
            "statement_period_end": self.statement_period_end.isoformat() if self.statement_period_end else None,
            "opening_balance": self.opening_balance,
            "closing_balance": self.closing_balance
        }


@dataclass
class ExtractionResult:
    """Result of extracting transactions from a statement."""
    transactions: List[Transaction]
    metadata: StatementMetadata
    extraction_method: ExtractionMethod
    confidence_score: float  # 0.0 to 1.0
    validation_passed: bool = False
    validation_errors: List[str] = field(default_factory=list)
    source_file: str = ""
    extracted_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "transactions": [t.to_dict() for t in self.transactions],
            "metadata": self.metadata.to_dict(),
            "extraction_method": self.extraction_method.value,
            "confidence_score": self.confidence_score,
            "validation_passed": self.validation_passed,
            "validation_errors": self.validation_errors,
            "source_file": self.source_file,
            "extracted_at": self.extracted_at.isoformat(),
            "transaction_count": len(self.transactions),
            "total_debits": sum(t.amount for t in self.transactions if t.amount < 0),
            "total_credits": sum(t.amount for t in self.transactions if t.amount > 0)
        }
