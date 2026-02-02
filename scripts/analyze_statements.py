#!/usr/bin/env python3
"""
Analyze all bank statements for discrepancies.
Processes all PDFs, extracts opening/closing balances, and finds mismatches.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from computare.extractors import HybridExtractor


def get_all_pdfs(base_dir: str = ".") -> list:
    """Find all PDF files in Scotiabank directories."""
    pdfs = []
    for item in os.listdir(base_dir):
        if "Scotiabank" in item and os.path.isdir(item):
            for f in os.listdir(item):
                if f.endswith(".pdf"):
                    pdfs.append(os.path.join(item, f))
    return sorted(pdfs)


def parse_statement_date(filename: str) -> tuple:
    """Extract month and year from filename like 'April 2024 e-statement.pdf'."""
    month_map = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    filename_lower = filename.lower()
    month = None
    year = None

    for month_name, month_num in month_map.items():
        if month_name in filename_lower:
            month = month_num
            break

    import re
    year_match = re.search(r'20\d{2}', filename)
    if year_match:
        year = int(year_match.group())

    return (year, month)


def main():
    print("=" * 70)
    print("BANK STATEMENT ANALYSIS")
    print("=" * 70)

    pdfs = get_all_pdfs()
    print(f"\nFound {len(pdfs)} PDF files\n")

    # Process each PDF
    extractor = HybridExtractor(enable_ai_fallback=False)
    results = []

    for pdf_path in pdfs:
        print(f"Processing: {pdf_path}... ", end="", flush=True)

        try:
            result = extractor.extract(pdf_path)

            # Get statement info
            year, month = parse_statement_date(pdf_path)

            # Get first and last transaction balances
            first_trans_balance = None
            last_trans_balance = None
            if result.transactions:
                first_trans_balance = result.transactions[0].balance
                last_trans_balance = result.transactions[-1].balance

            statement_info = {
                "file": pdf_path,
                "year": year,
                "month": month,
                "opening_balance": result.metadata.opening_balance,
                "closing_balance": result.metadata.closing_balance,
                "first_trans_balance": first_trans_balance,
                "last_trans_balance": last_trans_balance,
                "transaction_count": len(result.transactions),
                "total_debits": sum(t.amount for t in result.transactions if t.amount < 0),
                "total_credits": sum(t.amount for t in result.transactions if t.amount > 0),
                "confidence": result.confidence_score,
                "transactions": [t.to_dict() for t in result.transactions]
            }

            results.append(statement_info)
            print(f"OK ({len(result.transactions)} transactions)")

        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                "file": pdf_path,
                "error": str(e)
            })

    # Sort by date
    results = sorted(results, key=lambda x: (x.get("year", 0), x.get("month", 0)))

    # Save individual JSONs and combined result
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    for r in results:
        if "error" not in r:
            # Create filename from source
            basename = Path(r["file"]).stem
            out_path = output_dir / f"{basename}.json"
            with open(out_path, "w") as f:
                json.dump(r, f, indent=2, default=str)

    # Save combined analysis
    with open(output_dir / "all_statements_analysis.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    # Analyze discrepancies
    print("\n" + "=" * 70)
    print("DISCREPANCY ANALYSIS")
    print("=" * 70)

    discrepancies = []

    # Check 1: Statement opening/closing vs transaction balances
    print("\n--- Internal Consistency Checks ---")
    for r in results:
        if "error" in r:
            continue

        issues = []

        # Opening balance should match first transaction's starting balance
        # (first trans balance is AFTER that transaction, so we need to check against
        # what the balance would have been before)

        # Closing balance should match last transaction balance
        if r["closing_balance"] is not None and r["last_trans_balance"] is not None:
            if abs(r["closing_balance"] - r["last_trans_balance"]) > 0.01:
                issues.append(f"Closing balance mismatch: statement says ${r['closing_balance']:.2f}, last transaction shows ${r['last_trans_balance']:.2f}")

        if issues:
            discrepancies.append({
                "file": r["file"],
                "type": "internal",
                "issues": issues
            })
            print(f"\n{r['file']}:")
            for issue in issues:
                print(f"  - {issue}")

    # Check 2: Cross-statement continuity
    print("\n--- Cross-Statement Continuity ---")
    for i in range(1, len(results)):
        prev = results[i-1]
        curr = results[i]

        if "error" in prev or "error" in curr:
            continue

        # Previous closing should equal current opening
        if prev["closing_balance"] is not None and curr["opening_balance"] is not None:
            diff = abs(prev["closing_balance"] - curr["opening_balance"])
            if diff > 0.01:
                issue = f"Statement gap: {prev['file']} closes at ${prev['closing_balance']:.2f}, but {curr['file']} opens at ${curr['opening_balance']:.2f} (diff: ${diff:.2f})"
                discrepancies.append({
                    "type": "cross_statement",
                    "prev_file": prev["file"],
                    "curr_file": curr["file"],
                    "prev_closing": prev["closing_balance"],
                    "curr_opening": curr["opening_balance"],
                    "difference": diff
                })
                print(f"\n  {prev['file']} -> {curr['file']}:")
                print(f"    Prev closing: ${prev['closing_balance']:.2f}")
                print(f"    Curr opening: ${curr['opening_balance']:.2f}")
                print(f"    Difference: ${diff:.2f}")

    # Check 3: Zero-amount transactions
    print("\n--- Zero Amount Transactions ---")
    zero_amount_count = 0
    for r in results:
        if "error" in r:
            continue
        for t in r.get("transactions", []):
            if t["amount"] == 0:
                zero_amount_count += 1
                print(f"  {r['file']}: {t['date']} - {t['description'][:50]}")
    print(f"\nTotal zero-amount transactions: {zero_amount_count}")

    # Save discrepancies
    with open(output_dir / "discrepancies.json", "w") as f:
        json.dump(discrepancies, f, indent=2, default=str)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_trans = sum(r.get("transaction_count", 0) for r in results if "error" not in r)
    total_debits = sum(r.get("total_debits", 0) for r in results if "error" not in r)
    total_credits = sum(r.get("total_credits", 0) for r in results if "error" not in r)

    print(f"\nStatements processed: {len([r for r in results if 'error' not in r])}")
    print(f"Total transactions: {total_trans}")
    print(f"Total debits: ${abs(total_debits):,.2f}")
    print(f"Total credits: ${total_credits:,.2f}")
    print(f"Net change: ${total_debits + total_credits:,.2f}")
    print(f"\nDiscrepancies found: {len(discrepancies)}")
    print(f"Zero-amount transactions: {zero_amount_count}")

    if results:
        first = next((r for r in results if "error" not in r), None)
        last = next((r for r in reversed(results) if "error" not in r), None)
        if first and last:
            print(f"\nFirst statement opening balance: ${first['opening_balance']:.2f}" if first['opening_balance'] else "\nFirst statement opening balance: Not found")
            print(f"Last statement closing balance: ${last['closing_balance']:.2f}" if last['closing_balance'] else "Last statement closing balance: Not found")

    print(f"\nOutput saved to: {output_dir}/")
    print(f"  - Individual JSON files for each statement")
    print(f"  - all_statements_analysis.json (combined data)")
    print(f"  - discrepancies.json (issues found)")


if __name__ == "__main__":
    main()
