#!/usr/bin/env python3
"""
Analyze Wealthsimple CSV files and create a consolidated view.
"""

import os
import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEALTHSIMPLE_DIR = PROJECT_ROOT / "finances" / "Wealthsimple"
SUBFOLDER = WEALTHSIMPLE_DIR / "Wealthsimple Monthly Statements 2021-2026"

def parse_month_from_filename(filename: str) -> tuple[str, str, int, int] | None:
    """Extract account type, year, month from filename."""
    filename = filename.lower()

    # Pattern: 📈 Investments-2024-10-01-monthly-statement...
    if "investments-" in filename and "-monthly-statement" in filename:
        parts = filename.split("-")
        for i, p in enumerate(parts):
            if p.isdigit() and len(p) == 4:  # Year
                year = int(p)
                month = int(parts[i+1])
                return ("Investments (TFSA)", "subfolder", year, month)

    # Pattern: Investments Monthly Statement Oct 2024.csv
    if "investments monthly statement" in filename:
        parts = filename.replace(".csv", "").split()
        month_map = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                     "june": 6, "jul": 7, "july": 7, "aug": 8, "sept": 9, "sep": 9,
                     "oct": 10, "nov": 11, "dec": 12}
        for i, p in enumerate(parts):
            if p.lower() in month_map:
                month = month_map[p.lower()]
                year = int(parts[i+1])
                return ("Investments (TFSA)", "root", year, month)

    # Pattern: 💳 Spending-2024-12-01-monthly-statement...
    if "spending-" in filename and "-monthly-statement" in filename:
        parts = filename.split("-")
        for i, p in enumerate(parts):
            if p.isdigit() and len(p) == 4:
                year = int(p)
                month = int(parts[i+1])
                return ("Spending (Cash)", "subfolder", year, month)

    # Pattern: Wealthsimple Monthly Statement Dec 2024.csv or Wealthsimple Monthly Spending Statement
    if "wealthsimple monthly" in filename and "statement" in filename:
        parts = filename.replace(".csv", "").replace("(1)", "").split()
        month_map = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                     "june": 6, "jul": 7, "july": 7, "aug": 8, "sept": 9, "sep": 9,
                     "oct": 10, "nov": 11, "dec": 12}
        for i, p in enumerate(parts):
            if p.lower() in month_map and i+1 < len(parts):
                month = month_map[p.lower()]
                year_str = parts[i+1].strip()
                if year_str.isdigit():
                    year = int(year_str)
                    acct = "Spending (Cash)"
                    return (acct, "root", year, month)

    # Pattern: 🤖 Crypto-2025-08-01-monthly-statement...
    if "crypto-" in filename and "-monthly-statement" in filename:
        parts = filename.split("-")
        for i, p in enumerate(parts):
            if p.isdigit() and len(p) == 4:
                year = int(p)
                month = int(parts[i+1])
                return ("Crypto", "subfolder", year, month)

    # Pattern: Wealthsimple Crypto Monthly Statement Aug 2025.csv
    if "crypto monthly statement" in filename:
        parts = filename.replace(".csv", "").split()
        month_map = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                     "june": 6, "jul": 7, "july": 7, "aug": 8, "sept": 9, "sep": 9,
                     "oct": 10, "nov": 11, "dec": 12}
        for i, p in enumerate(parts):
            if p.lower() in month_map:
                month = month_map[p.lower()]
                year = int(parts[i+1])
                return ("Crypto", "root", year, month)

    # Credit card statements
    if "credit-card" in filename or "credit card" in filename:
        # Pattern: Wealthsimple-credit-card-2025-12-01...
        if "credit-card-" in filename:
            parts = filename.split("-")
            for i, p in enumerate(parts):
                if p.isdigit() and len(p) == 4:
                    year = int(p)
                    month = int(parts[i+1])
                    return ("Credit Card", "subfolder", year, month)
        # Pattern: Wealthsimple Credit Card Statement Dec 2025.csv
        else:
            parts = filename.replace(".csv", "").split()
            month_map = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                         "june": 6, "jul": 7, "july": 7, "aug": 8, "sept": 9, "sep": 9,
                         "oct": 10, "nov": 11, "dec": 12}
            for i, p in enumerate(parts):
                if p.lower() in month_map:
                    month = month_map[p.lower()]
                    year = int(parts[i+1])
                    return ("Credit Card", "root", year, month)

    return None

def count_transactions(filepath: Path) -> int:
    """Count non-header rows in CSV."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            # Subtract header row
            return max(0, len(rows) - 1)
    except Exception as e:
        return 0

def analyze_files():
    """Analyze all Wealthsimple CSV files."""
    # Structure: {account_type: {(year, month): {source: filepath, transactions: count}}}
    data = defaultdict(lambda: defaultdict(dict))

    # Analyze root folder files
    for f in WEALTHSIMPLE_DIR.glob("*.csv"):
        if f.stat().st_size == 0:
            continue
        parsed = parse_month_from_filename(f.name)
        if parsed:
            acct_type, source, year, month = parsed
            txn_count = count_transactions(f)
            key = (year, month)
            if "root" not in data[acct_type][key]:
                data[acct_type][key]["root"] = {"file": f.name, "transactions": txn_count}
            elif txn_count > data[acct_type][key]["root"]["transactions"]:
                # Keep the one with more transactions (handle duplicates like Feb 2025 (1))
                data[acct_type][key]["root"] = {"file": f.name, "transactions": txn_count}

    # Analyze subfolder files
    if SUBFOLDER.exists():
        for f in SUBFOLDER.glob("*.csv"):
            if f.stat().st_size == 0:
                continue
            parsed = parse_month_from_filename(f.name)
            if parsed:
                acct_type, source, year, month = parsed
                txn_count = count_transactions(f)
                key = (year, month)
                data[acct_type][key]["subfolder"] = {"file": f.name, "transactions": txn_count}

    return data

def analyze_activities_export():
    """Analyze the comprehensive activities export."""
    export_file = WEALTHSIMPLE_DIR / "Wealthsimple Activities Export Jan 18 2026.csv"
    if not export_file.exists():
        return None

    activities = defaultdict(lambda: defaultdict(int))  # {account_type: {(year, month): count}}
    date_range = {"min": None, "max": None}

    with open(export_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                date_str = row.get('transaction_date', '')
                if not date_str or date_str.startswith('"As of'):
                    continue
                date = datetime.strptime(date_str, '%Y-%m-%d')
                acct_type = row.get('account_type', 'Unknown')

                # Map account types
                acct_map = {"TFSA": "Investments (TFSA)", "Crypto": "Crypto"}
                acct_type = acct_map.get(acct_type, acct_type)

                activities[acct_type][(date.year, date.month)] += 1

                if date_range["min"] is None or date < date_range["min"]:
                    date_range["min"] = date
                if date_range["max"] is None or date > date_range["max"]:
                    date_range["max"] = date
            except (ValueError, KeyError):
                continue

    return {"activities": dict(activities), "date_range": date_range}

def main():
    print("=" * 80)
    print("WEALTHSIMPLE DATA ANALYSIS")
    print("=" * 80)

    data = analyze_files()
    activities = analyze_activities_export()

    # Print consolidated view by account type
    for acct_type in sorted(data.keys()):
        print(f"\n{'='*60}")
        print(f"📊 {acct_type}")
        print("="*60)

        months = sorted(data[acct_type].keys())

        if not months:
            print("  No monthly statement data found")
            continue

        # Get year range
        years = sorted(set(y for y, m in months))

        print(f"\n  Coverage: {years[0]} - {years[-1]}")
        print(f"  Months with data: {len(months)}")

        # Monthly breakdown
        print(f"\n  {'Month':<12} {'Root':<12} {'Subfolder':<12} {'Match?':<10}")
        print(f"  {'-'*12} {'-'*12} {'-'*12} {'-'*10}")

        mismatches = []
        missing_subfolder = []

        for year, month in months:
            month_name = datetime(year, month, 1).strftime("%b %Y")
            root_data = data[acct_type][(year, month)].get("root")
            sub_data = data[acct_type][(year, month)].get("subfolder")

            root_str = f"{root_data['transactions']} txn" if root_data else "❌ Missing"
            sub_str = f"{sub_data['transactions']} txn" if sub_data else "❌ Missing"

            if root_data and sub_data:
                if root_data['transactions'] == sub_data['transactions']:
                    match = "✅ Match"
                else:
                    match = "⚠️ Diff"
                    mismatches.append((year, month, root_data['transactions'], sub_data['transactions']))
            elif root_data and not sub_data:
                match = "📁 Root only"
                missing_subfolder.append((year, month))
            elif sub_data and not root_data:
                match = "📂 Sub only"
            else:
                match = "❓"

            print(f"  {month_name:<12} {root_str:<12} {sub_str:<12} {match:<10}")

        if mismatches:
            print(f"\n  ⚠️  Transaction count mismatches:")
            for y, m, r, s in mismatches:
                print(f"      {datetime(y, m, 1).strftime('%b %Y')}: Root={r}, Subfolder={s}")

        if missing_subfolder:
            print(f"\n  📁 Missing from subfolder (exists in root):")
            for y, m in missing_subfolder:
                print(f"      {datetime(y, m, 1).strftime('%b %Y')}")

    # Activities Export Analysis
    if activities:
        print(f"\n{'='*60}")
        print("📈 ACTIVITIES EXPORT ANALYSIS")
        print("="*60)
        print(f"\n  File: Wealthsimple Activities Export Jan 18 2026.csv")
        print(f"  Date Range: {activities['date_range']['min'].strftime('%Y-%m-%d')} to {activities['date_range']['max'].strftime('%Y-%m-%d')}")

        for acct_type, months in activities['activities'].items():
            total = sum(months.values())
            print(f"\n  {acct_type}: {total} activities")

            # Show by year
            by_year = defaultdict(int)
            for (y, m), count in months.items():
                by_year[y] += count
            for y in sorted(by_year.keys()):
                print(f"    {y}: {by_year[y]} activities")

    # Summary and recommendations
    print(f"\n{'='*60}")
    print("📋 SUMMARY & RECOMMENDATIONS")
    print("="*60)

    print("""
  1. MONTHLY STATEMENTS:
     - The subfolder "Wealthsimple Monthly Statements 2021-2026" contains
       organized statements starting from Oct 2024
     - The root folder has some additional/duplicate files with different naming
     - Many 2022-2023 files in root are EMPTY (0 bytes) - no actual data

  2. ACTIVITIES EXPORT:
     - "Wealthsimple Activities Export Jan 18 2026.csv" is a COMPREHENSIVE
       export covering ALL account activity from May 2021 to Jan 2026
     - This is the most complete data source

  3. DATA GAPS:
     - No monthly statement data exists for 2021-Sep 2024 (Investments)
     - But the Activities Export DOES contain this historical data!

  4. RECOMMENDATIONS:
     - Use the Activities Export as the primary data source for historical data
     - Use monthly statements for detailed transaction-level data (Oct 2024+)
     - The subfolder appears to be properly organized - use it as the canonical source
     - Root folder files can be archived/deleted as they're duplicates or empty
    """)

if __name__ == "__main__":
    main()
