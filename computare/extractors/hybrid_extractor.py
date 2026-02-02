"""
Hybrid extractor - combines pdfplumber with Claude AI fallback.
Uses fast local extraction first, falls back to AI for complex cases.
"""

from pathlib import Path
from typing import Optional

from .base import BaseExtractor
from .pdfplumber_extractor import PdfPlumberExtractor
from .claude_extractor import ClaudeExtractor
from ..models import ExtractionResult, ExtractionMethod
from ..config import CONFIDENCE_THRESHOLD, ANTHROPIC_API_KEY


class HybridExtractor(BaseExtractor):
    """
    Intelligent extractor that uses pdfplumber first,
    then falls back to Claude AI when confidence is low.
    """

    def __init__(
        self,
        confidence_threshold: float = CONFIDENCE_THRESHOLD,
        enable_ai_fallback: bool = True,
        api_key: Optional[str] = None
    ):
        """
        Initialize hybrid extractor.

        Args:
            confidence_threshold: Below this score, fall back to Claude
            enable_ai_fallback: Whether to use Claude when local extraction fails
            api_key: Anthropic API key (uses env var if not provided)
        """
        self.confidence_threshold = confidence_threshold
        self.enable_ai_fallback = enable_ai_fallback

        self.pdfplumber_extractor = PdfPlumberExtractor()

        # Only initialize Claude if fallback is enabled and API key available
        self.claude_extractor = None
        if enable_ai_fallback and (api_key or ANTHROPIC_API_KEY):
            try:
                self.claude_extractor = ClaudeExtractor(api_key=api_key)
            except ValueError:
                print("Warning: Claude fallback unavailable - no API key")

    def can_handle(self, pdf_path: str | Path) -> bool:
        """Check if any extractor can handle the PDF."""
        return self.pdfplumber_extractor.can_handle(pdf_path)

    def extract(self, pdf_path: str | Path, year: Optional[int] = None) -> ExtractionResult:
        """
        Extract transactions using hybrid approach.

        1. Try pdfplumber first (fast, free)
        2. If confidence < threshold, try Claude AI
        3. Return best result
        """
        pdf_path = Path(pdf_path)
        print(f"\n{'='*60}")
        print(f"Extracting: {pdf_path.name}")
        print(f"{'='*60}")

        # Step 1: Try pdfplumber
        print("Step 1: Attempting pdfplumber extraction...")
        pdfplumber_result = self.pdfplumber_extractor.extract(pdf_path, year)

        print(f"  - Transactions found: {len(pdfplumber_result.transactions)}")
        print(f"  - Confidence score: {pdfplumber_result.confidence_score:.2%}")

        # If confidence is good, return pdfplumber result
        if pdfplumber_result.confidence_score >= self.confidence_threshold:
            print(f"  - Confidence >= {self.confidence_threshold:.0%}, using pdfplumber result")
            return pdfplumber_result

        # Step 2: Check if we should fall back to Claude
        if not self.enable_ai_fallback:
            print("  - AI fallback disabled, returning pdfplumber result")
            return pdfplumber_result

        if not self.claude_extractor:
            print("  - Claude extractor not available, returning pdfplumber result")
            pdfplumber_result.validation_errors.append(
                "Low confidence but Claude fallback unavailable"
            )
            return pdfplumber_result

        # Step 3: Try Claude AI
        print(f"\nStep 2: Confidence {pdfplumber_result.confidence_score:.2%} < {self.confidence_threshold:.0%}")
        print("  - Falling back to Claude AI extraction...")

        try:
            claude_result = self.claude_extractor.extract(pdf_path, year)

            print(f"  - Claude transactions found: {len(claude_result.transactions)}")
            print(f"  - Claude confidence: {claude_result.confidence_score:.2%}")

            # Return Claude result if it found more transactions or has better confidence
            if len(claude_result.transactions) >= len(pdfplumber_result.transactions):
                print("  - Using Claude result")
                return claude_result
            else:
                print("  - pdfplumber found more transactions, using that result")
                return pdfplumber_result

        except Exception as e:
            print(f"  - Claude extraction failed: {e}")
            pdfplumber_result.validation_errors.append(f"Claude fallback failed: {e}")
            return pdfplumber_result

    def extract_with_comparison(
        self,
        pdf_path: str | Path,
        year: Optional[int] = None
    ) -> dict:
        """
        Extract using both methods and return comparison.
        Useful for debugging and validation.
        """
        pdf_path = Path(pdf_path)

        results = {
            "pdf_path": str(pdf_path),
            "pdfplumber": None,
            "claude": None,
            "recommended": None
        }

        # Extract with pdfplumber
        pdfplumber_result = self.pdfplumber_extractor.extract(pdf_path, year)
        results["pdfplumber"] = {
            "transaction_count": len(pdfplumber_result.transactions),
            "confidence": pdfplumber_result.confidence_score,
            "result": pdfplumber_result
        }

        # Extract with Claude if available
        if self.claude_extractor:
            try:
                claude_result = self.claude_extractor.extract(pdf_path, year)
                results["claude"] = {
                    "transaction_count": len(claude_result.transactions),
                    "confidence": claude_result.confidence_score,
                    "result": claude_result
                }
            except Exception as e:
                results["claude"] = {"error": str(e)}

        # Determine recommended result
        if results["claude"] and "result" in results["claude"]:
            # Compare and recommend
            pdf_count = results["pdfplumber"]["transaction_count"]
            claude_count = results["claude"]["transaction_count"]
            pdf_conf = results["pdfplumber"]["confidence"]
            claude_conf = results["claude"]["confidence"]

            if claude_count > pdf_count or (claude_count == pdf_count and claude_conf > pdf_conf):
                results["recommended"] = "claude"
            else:
                results["recommended"] = "pdfplumber"
        else:
            results["recommended"] = "pdfplumber"

        return results
