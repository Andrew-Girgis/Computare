#!/usr/bin/env python3
"""
Quick test script for Computare extraction.
Run this to test extraction on your Scotiabank e-statements.
"""

from pathlib import Path
from computare.batch_processor import BatchProcessor
from computare.extractors import HybridExtractor, PdfPlumberExtractor
from computare.validators import TransactionValidator
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_single_pdf():
    """Test extraction on a single PDF."""
    # Update this path to your actual statement PDF
    pdf_path = PROJECT_ROOT / "finances" / "Scotiabank" / "April 2024 e-statement.pdf"

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return

    print(f"\n{'='*70}")
    print("TESTING SINGLE PDF EXTRACTION")
    print(f"{'='*70}")

    # Test with pdfplumber only first
    print("\n--- Testing pdfplumber extraction ---")
    pdfplumber_extractor = PdfPlumberExtractor()
    result = pdfplumber_extractor.extract(pdf_path, year=2024)

    validator = TransactionValidator()
    result = validator.validate(result)

    print(f"\nTransactions found: {len(result.transactions)}")
    print(f"Confidence: {result.confidence_score:.1%}")
    print(f"Validation: {'PASSED' if result.validation_passed else 'FAILED'}")

    if result.transactions:
        print("\nFirst 5 transactions:")
        for trans in result.transactions[:5]:
            print(f"  {trans.date} | {trans.description[:30]:<30} | "
                  f"${trans.amount:>10,.2f} | Bal: ${trans.balance:,.2f}")

    if result.validation_errors:
        print(f"\nValidation issues ({len(result.validation_errors)}):")
        for err in result.validation_errors[:3]:
            print(f"  - {err}")

    # Save results
    output_path = pdf_path.with_suffix('.extracted.json')
    with open(output_path, 'w') as f:
        json.dump(result.to_dict(), f, indent=2, default=str)
    print(f"\nSaved to: {output_path}")

    return result


def test_hybrid_extraction():
    """Test hybrid extraction (pdfplumber + Claude fallback)."""
    pdf_path = PROJECT_ROOT / "finances" / "Scotiabank" / "April 2024 e-statement.pdf"

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return

    print(f"\n{'='*70}")
    print("TESTING HYBRID EXTRACTION (pdfplumber + Claude fallback)")
    print(f"{'='*70}")

    extractor = HybridExtractor(
        confidence_threshold=0.85,
        enable_ai_fallback=True  # Set to True if you have ANTHROPIC_API_KEY set
    )

    result = extractor.extract(pdf_path, year=2024)

    validator = TransactionValidator()
    result = validator.validate(result)

    summary = validator.get_summary(result)
    print(f"\n--- Summary ---")
    print(f"Method used: {result.extraction_method.value}")
    print(f"Transactions: {summary['transaction_count']}")
    print(f"Total Debits: ${summary['total_debits']:,.2f}")
    print(f"Total Credits: ${summary['total_credits']:,.2f}")
    print(f"Net Change: ${summary['net_change']:,.2f}")
    print(f"Validation: {'PASSED' if result.validation_passed else 'FAILED'}")

    return result


def test_batch_processing():
    """Test batch processing on a directory of PDFs."""
    statements_dir = PROJECT_ROOT / "finances" / "Scotiabank"

    if not statements_dir.exists():
        print(f"Directory not found: {statements_dir}")
        return

    print(f"\n{'='*70}")
    print("TESTING BATCH PROCESSING")
    print(f"{'='*70}")

    processor = BatchProcessor(
        enable_ai_fallback=False,  # Set to True if you have ANTHROPIC_API_KEY
        confidence_threshold=0.85
    )

    results = processor.process_directory(statements_dir, pattern="*.pdf", year=2024)
    report = processor.generate_report(results)

    print(f"\n--- Batch Report ---")
    print(f"Statements: {report['statements_processed']}")
    print(f"Validated: {report['statements_validated']}")
    print(f"Total Transactions: {report['total_transactions']}")
    print(f"Total Debits: ${report['total_debits']:,.2f}")
    print(f"Total Credits: ${report['total_credits']:,.2f}")

    # Save consolidated results
    output_path = statements_dir / "all_transactions_consolidated.json"
    processor.save_results(results, output_path, consolidated=True)

    return results


if __name__ == "__main__":
    print("="*70)
    print("COMPUTARE - Transaction Extraction Test Suite")
    print("="*70)

    # Run tests
    result = test_single_pdf()

    # Uncomment to test hybrid extraction (requires ANTHROPIC_API_KEY)
    # test_hybrid_extraction()

    # Uncomment to test batch processing
    # test_batch_processing()

    print("\n" + "="*70)
    print("Testing complete!")
    print("="*70)
