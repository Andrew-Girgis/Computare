"""
Batch processor for extracting transactions from multiple PDF statements.
"""

import json
from pathlib import Path
from typing import List, Optional, Generator
from datetime import datetime

from .extractors import HybridExtractor
from .validators import TransactionValidator
from .models import ExtractionResult, Transaction


class BatchProcessor:
    """
    Process multiple PDF statements and consolidate results.
    """

    def __init__(
        self,
        enable_ai_fallback: bool = True,
        confidence_threshold: float = 0.85,
        api_key: Optional[str] = None
    ):
        """
        Initialize batch processor.

        Args:
            enable_ai_fallback: Use Claude AI when local extraction fails
            confidence_threshold: Minimum confidence for pdfplumber results
            api_key: Anthropic API key
        """
        self.extractor = HybridExtractor(
            confidence_threshold=confidence_threshold,
            enable_ai_fallback=enable_ai_fallback,
            api_key=api_key
        )
        self.validator = TransactionValidator()

    def process_directory(
        self,
        directory: str | Path,
        pattern: str = "*.pdf",
        year: Optional[int] = None
    ) -> List[ExtractionResult]:
        """
        Process all PDFs in a directory.

        Args:
            directory: Path to directory containing PDFs
            pattern: Glob pattern for matching PDF files
            year: Default year for statements (auto-detects if not provided)

        Returns:
            List of ExtractionResult objects
        """
        directory = Path(directory)

        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        pdf_files = sorted(directory.glob(pattern))
        print(f"\nFound {len(pdf_files)} PDF files in {directory}")

        results = []
        for pdf_path in pdf_files:
            try:
                result = self.process_single(pdf_path, year)
                results.append(result)
            except Exception as e:
                print(f"Error processing {pdf_path.name}: {e}")
                # Create error result
                from .models import StatementMetadata, ExtractionMethod
                error_result = ExtractionResult(
                    transactions=[],
                    metadata=StatementMetadata(bank="unknown"),
                    extraction_method=ExtractionMethod.PDFPLUMBER,
                    confidence_score=0.0,
                    validation_errors=[f"Processing failed: {str(e)}"],
                    source_file=str(pdf_path)
                )
                results.append(error_result)

        return results

    def process_single(
        self,
        pdf_path: str | Path,
        year: Optional[int] = None
    ) -> ExtractionResult:
        """
        Process a single PDF file.

        Args:
            pdf_path: Path to PDF file
            year: Year for the statement

        Returns:
            ExtractionResult with validated transactions
        """
        # Extract
        result = self.extractor.extract(pdf_path, year)

        # Validate
        result = self.validator.validate(result)

        # Print summary
        summary = self.validator.get_summary(result)
        print(f"\n  Summary for {Path(pdf_path).name}:")
        print(f"    Transactions: {summary['transaction_count']}")
        print(f"    Total Debits: ${summary['total_debits']:,.2f}")
        print(f"    Total Credits: ${summary['total_credits']:,.2f}")
        print(f"    Net Change: ${summary['net_change']:,.2f}")
        print(f"    Validation: {'PASSED' if summary['validation_passed'] else 'FAILED'}")

        if not summary['validation_passed']:
            for error in summary['errors'][:3]:  # Show first 3 errors
                print(f"      - {error}")

        return result

    def consolidate_transactions(
        self,
        results: List[ExtractionResult]
    ) -> List[Transaction]:
        """
        Consolidate transactions from multiple statements.
        Removes duplicates and sorts by date.

        Args:
            results: List of extraction results

        Returns:
            Consolidated list of unique transactions sorted by date
        """
        all_transactions = []

        for result in results:
            all_transactions.extend(result.transactions)

        # Sort by date
        all_transactions.sort(key=lambda t: t.date)

        # Remove exact duplicates
        seen = set()
        unique_transactions = []

        for trans in all_transactions:
            # Create unique key
            key = (trans.date, trans.amount, trans.description[:20], trans.balance)

            if key not in seen:
                seen.add(key)
                unique_transactions.append(trans)

        return unique_transactions

    def save_results(
        self,
        results: List[ExtractionResult],
        output_path: str | Path,
        consolidated: bool = True
    ):
        """
        Save extraction results to JSON.

        Args:
            results: List of extraction results
            output_path: Path to output file
            consolidated: If True, consolidate all transactions into one file
        """
        output_path = Path(output_path)

        if consolidated:
            # Consolidate all transactions
            all_transactions = self.consolidate_transactions(results)

            output_data = {
                "extracted_at": datetime.now().isoformat(),
                "statement_count": len(results),
                "total_transactions": len(all_transactions),
                "transactions": [t.to_dict() for t in all_transactions],
                "statements": [
                    {
                        "source_file": r.source_file,
                        "transaction_count": len(r.transactions),
                        "validation_passed": r.validation_passed,
                        "confidence_score": r.confidence_score,
                        "extraction_method": r.extraction_method.value
                    }
                    for r in results
                ]
            }
        else:
            # Save each result separately
            output_data = {
                "extracted_at": datetime.now().isoformat(),
                "results": [r.to_dict() for r in results]
            }

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)

        print(f"\nResults saved to: {output_path}")

    def generate_report(self, results: List[ExtractionResult]) -> dict:
        """
        Generate a summary report of all processed statements.
        """
        all_transactions = self.consolidate_transactions(results)

        total_debits = sum(t.amount for t in all_transactions if t.amount < 0)
        total_credits = sum(t.amount for t in all_transactions if t.amount > 0)

        passed_count = sum(1 for r in results if r.validation_passed)

        # Get date range
        dates = [t.date for t in all_transactions]
        date_range = {
            "start": min(dates).isoformat() if dates else None,
            "end": max(dates).isoformat() if dates else None
        }

        return {
            "statements_processed": len(results),
            "statements_validated": passed_count,
            "total_transactions": len(all_transactions),
            "total_debits": round(total_debits, 2),
            "total_credits": round(total_credits, 2),
            "net_change": round(total_debits + total_credits, 2),
            "date_range": date_range,
            "extraction_methods": {
                method: sum(1 for r in results if r.extraction_method.value == method)
                for method in set(r.extraction_method.value for r in results)
            }
        }
