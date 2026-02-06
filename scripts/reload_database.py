#!/usr/bin/env python3
"""
Reload all financial data into the local Supabase database.

Safe to run after `supabase db reset` — re-imports everything from
the extracted JSON files in output/.

Usage:
    python scripts/reload_database.py              # Load data (skip if tables have data)
    python scripts/reload_database.py --force      # Wipe transactions and reload
    python scripts/reload_database.py --reset      # Run supabase db reset first, then load
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from computare.database.loader import DatabaseLoader


OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def check_existing_data(loader: DatabaseLoader) -> int:
    """Return current transaction count."""
    try:
        result = loader.client.table("transactions").select("id", count="exact").limit(1).execute()
        return result.count or 0
    except Exception:
        return 0


def clear_data(loader: DatabaseLoader):
    """Delete all transactions, statements, trade_details (cascade handles FKs)."""
    print("Clearing existing data...")
    for table in ["trade_details", "transactions", "statements", "subscriptions", "merchant_cache", "holdings"]:
        try:
            # Delete all rows — Supabase client needs a filter, use gt on created_at epoch
            loader.client.table(table).delete().gte("created_at", "1970-01-01").execute()
        except Exception as e:
            print(f"  Warning: Could not clear {table}: {e}")
    # Clear accounts and institutions last (FK ordering)
    for table in ["accounts", "institutions"]:
        try:
            loader.client.table(table).delete().gte("created_at", "1970-01-01").execute()
        except Exception as e:
            print(f"  Warning: Could not clear {table}: {e}")
    print("  Done.")


def run_db_reset():
    """Run supabase db reset to rebuild schema from migrations."""
    print("Running supabase db reset...")
    result = subprocess.run(
        ["supabase", "db", "reset"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
        sys.exit(1)
    print("  Schema reset complete.")


def main():
    parser = argparse.ArgumentParser(description="Reload financial data into Supabase")
    parser.add_argument("--force", action="store_true", help="Clear existing data before loading")
    parser.add_argument("--reset", action="store_true", help="Run supabase db reset first")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Path to output directory")
    args = parser.parse_args()

    if not args.output_dir.exists():
        print(f"Error: Output directory not found: {args.output_dir}")
        sys.exit(1)

    if args.reset:
        run_db_reset()

    print(f"\n{'='*50}")
    print("COMPUTARE — Database Reload")
    print(f"{'='*50}")
    print(f"Source: {args.output_dir}")

    loader = DatabaseLoader()
    if not loader.connect():
        sys.exit(1)

    existing = check_existing_data(loader)
    if existing > 0 and not args.force and not args.reset:
        print(f"\nDatabase already has {existing:,} transactions.")
        print("Use --force to clear and reload, or --reset to rebuild schema.")
        sys.exit(0)

    if args.force and not args.reset:
        clear_data(loader)

    results = loader.load_all(args.output_dir)

    if results:
        total = sum(results.values())
        print(f"\nReload complete: {total:,} transactions across {len(results)} sources.")
    else:
        print("\nNo data loaded. Check your output directory and .env configuration.")


if __name__ == "__main__":
    main()
