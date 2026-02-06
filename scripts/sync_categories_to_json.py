#!/usr/bin/env python3
"""
Sync categories from the Supabase merchant_cache back to JSON files.

After running LLM categorization, this script reads the cached categories
from the database and updates the local JSON files so they survive db resets.

Usage:
    python scripts/sync_categories_to_json.py           # Sync all
    python scripts/sync_categories_to_json.py --dry-run # Preview changes
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional

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


def load_merchant_cache() -> Dict[str, Dict]:
    """
    Load the merchant_cache table from Supabase.

    Returns dict mapping raw_store -> {category, normalized_merchant, sub_category}
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set")
        sys.exit(1)

    client = create_client(url, key)

    # Fetch all entries from merchant_cache
    cache = {}
    offset = 0
    page_size = 1000

    while True:
        result = client.table('merchant_cache').select(
            'raw_store,normalized_merchant,category,sub_category'
        ).range(offset, offset + page_size - 1).execute()

        if not result.data:
            break

        for row in result.data:
            raw_store = row.get('raw_store')
            if raw_store:
                cache[raw_store] = {
                    'category': row.get('category'),
                    'merchant': row.get('normalized_merchant'),
                    'sub_category': row.get('sub_category'),
                }

        if len(result.data) < page_size:
            break
        offset += page_size

    return cache


def sync_file(
    json_path: Path,
    cache: Dict[str, Dict],
    dry_run: bool = False,
) -> Dict[str, int]:
    """
    Sync categories from cache to a single JSON file.

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
        # Try to match against cache using various keys
        raw_store = txn.get("store", "")
        description = txn.get("description", "")

        # Try raw_store first, then description
        cache_entry = None
        for key in [raw_store, description]:
            if key and key in cache:
                cache_entry = cache[key]
                break

        if cache_entry:
            updated = False

            # Update category if cache has one and txn doesn't (or is different)
            if cache_entry.get('category') and txn.get('category') != cache_entry['category']:
                if not txn.get('category'):
                    txn['category'] = cache_entry['category']
                    updated = True

            # Update merchant if cache has one
            if cache_entry.get('merchant') and txn.get('merchant') != cache_entry['merchant']:
                if not txn.get('merchant'):
                    txn['merchant'] = cache_entry['merchant']
                    updated = True

            # Update sub_category if cache has one
            if cache_entry.get('sub_category') and txn.get('sub_category') != cache_entry['sub_category']:
                if not txn.get('sub_category'):
                    txn['sub_category'] = cache_entry['sub_category']
                    updated = True

            if updated:
                stats["updated"] += 1
                file_modified = True
            elif txn.get('category'):
                stats["already_had"] += 1
            else:
                stats["no_match"] += 1
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
    cache: Dict[str, Dict],
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
        stats = sync_file(json_file, cache, dry_run=dry_run)

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
    parser = argparse.ArgumentParser(description="Sync categories from DB to JSON files")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()

    if not args.output_dir.exists():
        print(f"Error: Output directory not found: {args.output_dir}")
        sys.exit(1)

    print(f"{'='*60}")
    print("COMPUTARE — Sync Categories from DB to JSON")
    print(f"{'='*60}")
    print(f"Target: {args.output_dir}")
    if args.dry_run:
        print("Mode: DRY RUN (no files will be modified)")
    print()

    print("Loading merchant cache from database...")
    cache = load_merchant_cache()
    print(f"  Loaded {len(cache):,} cached entries")
    print()

    totals = sync_directory(args.output_dir, cache, dry_run=args.dry_run)

    print()
    print(f"{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"Files processed:     {totals['files']}")
    print(f"Transactions total:  {totals['total']:,}")
    print(f"Updated from cache:  {totals['updated']:,}")
    print(f"Already categorized: {totals['already_had']:,}")
    print(f"No cache match:      {totals['no_match']:,}")

    categorized = totals['updated'] + totals['already_had']
    pct = categorized / max(totals['total'], 1) * 100
    print(f"Total with category: {categorized:,} ({pct:.1f}%)")

    if args.dry_run:
        print("\nRun without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
