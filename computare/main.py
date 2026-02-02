"""
Computare - Main entry point for transaction extraction.
"""

import argparse
import json
import sys
from pathlib import Path

from .batch_processor import BatchProcessor
from .extractors import HybridExtractor
from .validators import TransactionValidator


def extract_single(pdf_path: str, year: int = None, output: str = None, use_ai: bool = True):
    """Extract transactions from a single PDF."""
    extractor = HybridExtractor(enable_ai_fallback=use_ai)
    validator = TransactionValidator()

    result = extractor.extract(pdf_path, year)
    result = validator.validate(result)

    # Print results
    summary = validator.get_summary(result)

    print(f"\n{'='*60}")
    print("EXTRACTION SUMMARY")
    print(f"{'='*60}")
    print(f"File: {pdf_path}")
    print(f"Bank: {result.metadata.bank}")
    print(f"Method: {result.extraction_method.value}")
    print(f"Confidence: {result.confidence_score:.1%}")
    print(f"Transactions: {len(result.transactions)}")
    print(f"Total Debits: ${summary['total_debits']:,.2f}")
    print(f"Total Credits: ${summary['total_credits']:,.2f}")
    print(f"Net Change: ${summary['net_change']:,.2f}")
    print(f"Validation: {'PASSED' if result.validation_passed else 'FAILED'}")

    if result.validation_errors:
        print(f"\nValidation Errors ({len(result.validation_errors)}):")
        for error in result.validation_errors[:5]:
            print(f"  - {error}")
        if len(result.validation_errors) > 5:
            print(f"  ... and {len(result.validation_errors) - 5} more")

    # Save to file
    if output:
        output_path = Path(output)
    else:
        output_path = Path(pdf_path).with_suffix('.json')

    with open(output_path, 'w') as f:
        json.dump(result.to_dict(), f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")

    # Print sample transactions
    print(f"\n{'='*60}")
    print("SAMPLE TRANSACTIONS (first 5)")
    print(f"{'='*60}")
    for trans in result.transactions[:5]:
        print(f"  {trans.date} | {trans.description[:35]:<35} | "
              f"${trans.amount:>10,.2f} | Balance: ${trans.balance:,.2f}")

    return result


def extract_batch(directory: str, pattern: str = "*.pdf", year: int = None,
                  output: str = None, use_ai: bool = True):
    """Extract transactions from all PDFs in a directory."""
    processor = BatchProcessor(enable_ai_fallback=use_ai)

    results = processor.process_directory(directory, pattern, year)
    report = processor.generate_report(results)

    print(f"\n{'='*60}")
    print("BATCH PROCESSING REPORT")
    print(f"{'='*60}")
    print(f"Statements Processed: {report['statements_processed']}")
    print(f"Statements Validated: {report['statements_validated']}")
    print(f"Total Transactions: {report['total_transactions']}")
    print(f"Total Debits: ${report['total_debits']:,.2f}")
    print(f"Total Credits: ${report['total_credits']:,.2f}")
    print(f"Net Change: ${report['net_change']:,.2f}")
    print(f"Date Range: {report['date_range']['start']} to {report['date_range']['end']}")

    # Save results
    if output:
        output_path = Path(output)
    else:
        output_path = Path(directory) / "all_transactions.json"

    processor.save_results(results, output_path, consolidated=True)

    return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Computare - Extract transactions from bank e-statements"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Single file extraction
    single_parser = subparsers.add_parser("extract", help="Extract from single PDF")
    single_parser.add_argument("pdf_path", help="Path to PDF file")
    single_parser.add_argument("--year", "-y", type=int, help="Statement year")
    single_parser.add_argument("--output", "-o", help="Output JSON file path")
    single_parser.add_argument("--no-ai", action="store_true",
                               help="Disable Claude AI fallback")

    # Batch extraction
    batch_parser = subparsers.add_parser("batch", help="Extract from directory of PDFs")
    batch_parser.add_argument("directory", help="Directory containing PDF files")
    batch_parser.add_argument("--pattern", "-p", default="*.pdf",
                              help="Glob pattern for PDF files (default: *.pdf)")
    batch_parser.add_argument("--year", "-y", type=int, help="Statement year")
    batch_parser.add_argument("--output", "-o", help="Output JSON file path")
    batch_parser.add_argument("--no-ai", action="store_true",
                              help="Disable Claude AI fallback")

    args = parser.parse_args()

    if args.command == "extract":
        extract_single(args.pdf_path, args.year, args.output, not args.no_ai)
    elif args.command == "batch":
        extract_batch(args.directory, args.pattern, args.year, args.output, not args.no_ai)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
