#!/usr/bin/env python3
"""
Export categories from Supabase transactions back to JSON files.

This script reads categorized transactions from the database and matches them
back to the JSON files by date, amount, and description to update the local files.

Usage:
    python scripts/export_categories_from_db.py           # Export all
    python scripts/export_categories_from_db.py --dry-run # Preview changes
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

# Files to skip (aggregates, not statement data)
SKIP_FILES = {
    "all_transactions.json",
    "all_statements_analysis.json",
    "discrepancies.json",
    "financial_summary.json",
}


def make_txn_key(date: str, amount: float, description: str) -> str:
    """Create a unique key for matching transactions."""
    # Normalize amount to 2 decimal places
    amt_str = f"{float(amount):.2f}"
    # Use first 50 chars of description to handle truncation
    desc_key = (description or "")[:50].lower().strip()
    return f"{date}|{amt_str}|{desc_key}"


def load_db_transactions() -> Dict[str, Dict]:
    """
    Load categorized transactions from Supabase.

    Returns dict mapping txn_key -> {category, merchant, sub_category}
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set")
        sys.exit(1)

    client = create_client(url, key)

    # Fetch all transactions with categories
    txn_map = {}
    offset = 0
    page_size = 1000

    while True:
        result = client.table('transactions').select(
            'date,amount,description,category,merchant,sub_category'
        ).not_.is_('category', 'null').range(offset, offset + page_size - 1).execute()

        if not result.data:
            break

        for row in result.data:
            date = row.get('date', '')
            # Handle date string format
            if date and 'T' in date:
                date = date.split('T')[0]

            amount = float(row.get('amount', 0))
            description = row.get('description', '')

            key = make_txn_key(date, amount, description)
            txn_map[key] = {
                'category': row.get('category'),
                'merchant': row.get('merchant'),
                'sub_category': row.get('sub_category'),
            }

        if len(result.data) < page_size:
            break
        offset += page_size

    return txn_map


def sync_file(
    json_path: Path,
    db_txns: Dict[str, Dict],
    dry_run: bool = False,
) -> Dict[str, int]:
    """
    Sync categories from DB to a single JSON file.

    Returns dict with counts: {total, updated, already_had, no_match}
    """
    stats = {"total": 0, "updated": 0, "already_had": 0, "no_match": 0}

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
        # Build key from JSON transaction
        date = txn.get("date", "")
        amount = txn.get("amount", 0)
        # Use description for matching
        description = txn.get("description", "") or txn.get("store", "")

        key = make_txn_key(date, amount, description)
        db_entry = db_txns.get(key)

        if db_entry:
            updated = False

            # Update category if DB has one and JSON doesn't
            if db_entry.get('category') and not txn.get('category'):
                txn['category'] = db_entry['category']
                updated = True

            # Update merchant if DB has one and JSON doesn't
            if db_entry.get('merchant') and not txn.get('merchant'):
                txn['merchant'] = db_entry['merchant']
                updated = True

            # Update sub_category if DB has one and JSON doesn't
            if db_entry.get('sub_category') and not txn.get('sub_category'):
                txn['sub_category'] = db_entry['sub_category']
                updated = True

            if updated:
                stats["updated"] += 1
                file_modified = True
            else:
                stats["already_had"] += 1
        else:
            if txn.get('category'):
                stats["already_had"] += 1
            else:
                stats["no_match"] += 1

    if file_modified and not dry_run:
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

    return stats


def sync_directory(
    output_dir: Path,
    db_txns: Dict[str, Dict],
    dry_run: bool = False,
) -> Dict[str, int]:
    """
    Sync categories for all JSON files in directory.

    Returns aggregated stats.
    """
    totals = {"files": 0, "total": 0, "updated": 0, "already_had": 0, "no_match": 0}

    # Find all JSON files recursively
    json_files = list(output_dir.rglob("*.json"))

    # Skip aggregate files
    json_files = [f for f in json_files if f.name not in SKIP_FILES]

    for json_file in sorted(json_files):
        stats = sync_file(json_file, db_txns, dry_run=dry_run)

        if stats["total"] > 0:
            totals["files"] += 1
            totals["total"] += stats["total"]
            totals["updated"] += stats["updated"]
            totals["already_had"] += stats["already_had"]
            totals["no_match"] += stats["no_match"]

            if stats["updated"] > 0:
                rel_path = json_file.relative_to(output_dir)
                print(f"  {rel_path}: {stats['updated']}/{stats['total']} updated")

    return totals


def main():
    parser = argparse.ArgumentParser(description="Export categories from DB to JSON files")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()

    if not args.output_dir.exists():
        print(f"Error: Output directory not found: {args.output_dir}")
        sys.exit(1)

    print(f"{'='*60}")
    print("COMPUTARE — Export Categories from DB to JSON")
    print(f"{'='*60}")
    print(f"Target: {args.output_dir}")
    if args.dry_run:
        print("Mode: DRY RUN (no files will be modified)")
    print()

    print("Loading categorized transactions from database...")
    db_txns = load_db_transactions()
    print(f"  Loaded {len(db_txns):,} categorized transactions")
    print()

    totals = sync_directory(args.output_dir, db_txns, dry_run=args.dry_run)

    print()
    print(f"{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"Files processed:     {totals['files']}")
    print(f"Transactions total:  {totals['total']:,}")
    print(f"Updated from DB:     {totals['updated']:,}")
    print(f"Already categorized: {totals['already_had']:,}")
    print(f"No DB match:         {totals['no_match']:,}")

    categorized = totals['updated'] + totals['already_had']
    pct = categorized / max(totals['total'], 1) * 100
    print(f"Total with category: {categorized:,} ({pct:.1f}%)")

    if args.dry_run:
        print("\nRun without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
