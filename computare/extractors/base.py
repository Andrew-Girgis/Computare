"""
Base extractor interface.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path

from ..models import Transaction, ExtractionResult, StatementMetadata


class BaseExtractor(ABC):
    """Abstract base class for all extractors."""

    @abstractmethod
    def extract(self, pdf_path: str | Path, year: Optional[int] = None) -> ExtractionResult:
        """
        Extract transactions from a PDF statement.

        Args:
            pdf_path: Path to the PDF file
            year: Year of the statement (for date formatting if not detectable)

        Returns:
            ExtractionResult containing transactions and metadata
        """
        pass

    @abstractmethod
    def can_handle(self, pdf_path: str | Path) -> bool:
        """
        Check if this extractor can handle the given PDF.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            True if this extractor can handle the PDF
        """
        pass

    def detect_bank(self, text: str) -> Optional[str]:
        """Detect the bank from PDF text content."""
        from ..config import BANK_PATTERNS

        text_lower = text.lower()
        for bank, patterns in BANK_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    return bank
        return None
