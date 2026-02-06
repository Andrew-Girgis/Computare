#!/usr/bin/env python3
"""
Enrich extracted JSON files with normalized merchants and categories.

Reads JSON files from output/, applies the categorization pipeline,
and writes enriched data back to the same files.

This makes the JSON files the source of truth — after running this script,
`reload_database.py` will populate a fully categorized database without
needing to re-run the LLM categorizer.

Usage:
    python scripts/enrich_json.py                    # Enrich all JSON files
    python scripts/enrich_json.py --dry-run          # Preview changes without writing
    python scripts/enrich_json.py --file "Jan*.json" # Enrich specific files (glob pattern)
    python scripts/enrich_json.py --force            # Re-categorize even if already enriched
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from fnmatch import fnmatch

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from computare.categorizer.normalizer import normalize_merchant
from computare.categorizer.categories import (
    KNOWN_MERCHANT_HINTS,
    DESCRIPTION_CATEGORY_RULES,
    TransactionCategory,
)
from computare.categorizer.normalizer import CANONICAL_MERCHANT_NAMES


OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

# Files to skip (aggregates, not statement data)
SKIP_FILES = {
    "all_transactions.json",
    "all_statements_analysis.json",
    "discrepancies.json",
    "financial_summary.json",
}


def match_known_merchant(
    raw_store: str, description: str, transaction_type: str = ""
) -> Optional[Tuple[str, str, Optional[str]]]:
    """
    Match against known merchant keywords.

    Returns (normalized_merchant, category, sub_category) or None.
    """
    # Check transaction_type (Wealthsimple activity types like BUY, SELL, CONT)
    if transaction_type and transaction_type in DESCRIPTION_CATEGORY_RULES:
        cat, sub_cat = DESCRIPTION_CATEGORY_RULES[transaction_type]
        return transaction_type, cat.value, sub_cat.value if sub_cat else None

    # Check description-based rules (Payrolldep -> Income)
    if description in DESCRIPTION_CATEGORY_RULES:
        cat, sub_cat = DESCRIPTION_CATEGORY_RULES[description]
        return description, cat.value, sub_cat.value if sub_cat else None

    # Check for investment activity patterns in description (BUY STOCK, SELL STOCK, DIV, etc.)
    desc_upper = description.upper() if description else ""
    for activity in ['BUY', 'SELL', 'DIV', 'DIVIDEND', 'CONT', 'CONTRIBUTION', 'WITHDRAW', 'WITHDRAWAL', 'FEE']:
        if desc_upper.startswith(activity + ' ') or desc_upper.startswith(activity + '('):
            if activity in DESCRIPTION_CATEGORY_RULES:
                cat, sub_cat = DESCRIPTION_CATEGORY_RULES[activity]
                return activity, cat.value, sub_cat.value if sub_cat else None

    # Try raw_store first, then description (credit card uses description as merchant)
    search_strings = []
    if raw_store:
        search_strings.append(raw_store)
    if description and description != raw_store:
        search_strings.append(description)

    if not search_strings:
        return None

    # Try to match each search string
    for search_str in search_strings:
        normalized = normalize_merchant(search_str)
        normalized_lower = normalized.lower()
        search_lower = search_str.lower()

        for keyword, (category, sub_cat) in KNOWN_MERCHANT_HINTS.items():
            if keyword in normalized_lower or keyword in search_lower:
                sub_value = sub_cat.value if sub_cat else None
                display_name = CANONICAL_MERCHANT_NAMES.get(keyword, normalized)
                return display_name, category.value, sub_value

    # No match — normalize the best available string
    best_str = raw_store or description
    return normalize_merchant(best_str), None, None


def enrich_transaction(txn: Dict, force: bool = False) -> Tuple[Dict, bool]:
    """
    Enrich a single transaction with normalized merchant and category.

    Handles both chequing format (store field) and credit card format (description as merchant).

    Returns (enriched_txn, was_modified).
    """
    modified = False

    # Chequing has 'store', credit card has merchant info in 'description'
    # Wealthsimple has 'transaction_type' for activity type (BUY, SELL, CONT, etc.)
    raw_store = txn.get("store", "")
    description = txn.get("description", "")
    transaction_type = txn.get("transaction_type", "")

    # Skip if already enriched (unless force)
    if not force and txn.get("merchant") and txn.get("category"):
        return txn, False

    result = match_known_merchant(raw_store, description, transaction_type)

    if result:
        merchant, category, sub_category = result

        # Update merchant if not set or different
        if txn.get("merchant") != merchant:
            txn["merchant"] = merchant
            modified = True

        # Update category if matched and not already set
        if category and txn.get("category") != category:
            txn["category"] = category
            modified = True

        # Update sub_category if matched
        if sub_category and txn.get("sub_category") != sub_category:
            txn["sub_category"] = sub_category
            modified = True

    elif raw_store and not txn.get("merchant"):
        # No category match but normalize merchant anyway
        txn["merchant"] = normalize_merchant(raw_store)
        modified = True

    return txn, modified


def enrich_file(
    json_path: Path,
    dry_run: bool = False,
    force: bool = False,
) -> Dict[str, int]:
    """
    Enrich a single JSON file.

    Returns dict with counts: {total, enriched, categorized, skipped}.
    """
    stats = {"total": 0, "enriched": 0, "categorized": 0, "skipped": 0}

    try:
        with open(json_path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"  Error reading {json_path.name}: {e}")
        return stats

    if "transactions" not in data:
        return stats

    transactions = data["transactions"]
    stats["total"] = len(transactions)
    file_modified = False

    for txn in transactions:
        txn, was_modified = enrich_transaction(txn, force=force)

        if was_modified:
            stats["enriched"] += 1
            file_modified = True

        if txn.get("category"):
            stats["categorized"] += 1
        else:
            stats["skipped"] += 1

    if file_modified and not dry_run:
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

    return stats


def enrich_directory(
    output_dir: Path,
    file_pattern: Optional[str] = None,
    dry_run: bool = False,
    force: bool = False,
    subdirs: bool = True,
) -> Dict[str, int]:
    """
    Enrich all JSON files in a directory.

    Returns aggregated stats.
    """
    totals = {"files": 0, "total": 0, "enriched": 0, "categorized": 0, "skipped": 0}

    # Find all JSON files
    if subdirs:
        json_files = list(output_dir.rglob("*.json"))
    else:
        json_files = list(output_dir.glob("*.json"))

    # Filter by pattern if specified
    if file_pattern:
        json_files = [f for f in json_files if fnmatch(f.name, file_pattern)]

    # Skip aggregate files
    json_files = [f for f in json_files if f.name not in SKIP_FILES]

    for json_file in sorted(json_files):
        stats = enrich_file(json_file, dry_run=dry_run, force=force)

        if stats["total"] > 0:
            totals["files"] += 1
            totals["total"] += stats["total"]
            totals["enriched"] += stats["enriched"]
            totals["categorized"] += stats["categorized"]
            totals["skipped"] += stats["skipped"]

            if stats["enriched"] > 0:
                rel_path = json_file.relative_to(output_dir)
                print(f"  {rel_path}: {stats['enriched']}/{stats['total']} enriched")

    return totals


def main():
    parser = argparse.ArgumentParser(description="Enrich JSON files with categories")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--force", action="store_true", help="Re-categorize already enriched transactions")
    parser.add_argument("--file", type=str, help="File pattern to match (e.g., 'Jan*.json')")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()

    if not args.output_dir.exists():
        print(f"Error: Output directory not found: {args.output_dir}")
        sys.exit(1)

    print(f"{'='*60}")
    print("COMPUTARE — JSON Enrichment")
    print(f"{'='*60}")
    print(f"Source: {args.output_dir}")
    if args.dry_run:
        print("Mode: DRY RUN (no files will be modified)")
    if args.force:
        print("Mode: FORCE (re-categorizing already enriched)")
    print()

    totals = enrich_directory(
        args.output_dir,
        file_pattern=args.file,
        dry_run=args.dry_run,
        force=args.force,
    )

    print()
    print(f"{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"Files processed:     {totals['files']}")
    print(f"Transactions total:  {totals['total']:,}")
    print(f"Transactions enriched: {totals['enriched']:,}")
    print(f"With category:       {totals['categorized']:,} ({totals['categorized']/max(totals['total'],1)*100:.1f}%)")
    print(f"Needs LLM:           {totals['skipped']:,} ({totals['skipped']/max(totals['total'],1)*100:.1f}%)")

    if args.dry_run:
        print("\nRun without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
