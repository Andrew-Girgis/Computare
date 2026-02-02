#!/usr/bin/env python3
"""
Analyze American Express CSV files and create a consolidated view.
"""

import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AMEX_DIR = PROJECT_ROOT / "finances" / "American Express"

def parse_amount(value: str) -> Decimal:
    """Parse amount string to Decimal."""
    if not value or not value.strip():
        return Decimal('0')
    # Remove commas and convert
    return Decimal(value.replace(',', '').strip())

def parse_date(date_str: str) -> datetime | None:
    """Parse date in DD/MM/YYYY format."""
    try:
        return datetime.strptime(date_str.strip(), '%d/%m/%Y')
    except (ValueError, AttributeError):
        return None

def analyze_file(filepath: Path) -> dict:
    """Analyze a single AMEX CSV file."""
    transactions = []
    categories = defaultdict(lambda: {'charges': Decimal('0'), 'credits': Decimal('0'), 'count': 0})
    subcategories = defaultdict(lambda: {'charges': Decimal('0'), 'credits': Decimal('0'), 'count': 0})
    monthly = defaultdict(lambda: {'charges': Decimal('0'), 'credits': Decimal('0'), 'count': 0})

    total_charges = Decimal('0')
    total_credits = Decimal('0')
    date_range = {'min': None, 'max': None}

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = parse_date(row.get('Date', ''))
            if not date:
                continue

            charges = parse_amount(row.get('Charges $', ''))
            credits = parse_amount(row.get('Credits $', ''))
            category = row.get('Category', 'Unknown')
            subcategory = row.get('Sub-Category', 'Unknown')
            transaction = row.get('Transaction', '')
            month_billed = row.get('Month-Billed', '')

            transactions.append({
                'date': date,
                'category': category,
                'subcategory': subcategory,
                'transaction': transaction,
                'charges': charges,
                'credits': credits,
                'month_billed': month_billed
            })

            # Aggregate by category
            categories[category]['charges'] += charges
            categories[category]['credits'] += credits
            categories[category]['count'] += 1

            # Aggregate by subcategory
            subcategories[subcategory]['charges'] += charges
            subcategories[subcategory]['credits'] += credits
            subcategories[subcategory]['count'] += 1

            # Aggregate by month (transaction date)
            month_key = (date.year, date.month)
            monthly[month_key]['charges'] += charges
            monthly[month_key]['credits'] += credits
            monthly[month_key]['count'] += 1

            total_charges += charges
            total_credits += credits

            if date_range['min'] is None or date < date_range['min']:
                date_range['min'] = date
            if date_range['max'] is None or date > date_range['max']:
                date_range['max'] = date

    return {
        'transactions': transactions,
        'categories': dict(categories),
        'subcategories': dict(subcategories),
        'monthly': dict(monthly),
        'total_charges': total_charges,
        'total_credits': total_credits,
        'net': total_charges - total_credits,
        'count': len(transactions),
        'date_range': date_range
    }

def main():
    print("=" * 80)
    print("AMERICAN EXPRESS DATA ANALYSIS")
    print("=" * 80)

    files = sorted(AMEX_DIR.glob("*.csv"))

    all_data = {}
    combined_categories = defaultdict(lambda: {'charges': Decimal('0'), 'credits': Decimal('0'), 'count': 0})
    combined_subcategories = defaultdict(lambda: {'charges': Decimal('0'), 'credits': Decimal('0'), 'count': 0})
    combined_monthly = defaultdict(lambda: {'charges': Decimal('0'), 'credits': Decimal('0'), 'count': 0})
    grand_charges = Decimal('0')
    grand_credits = Decimal('0')
    grand_count = 0
    overall_date_range = {'min': None, 'max': None}

    for f in files:
        print(f"\n{'='*60}")
        print(f"📄 {f.name}")
        print("=" * 60)

        data = analyze_file(f)
        all_data[f.name] = data

        # Print file summary
        print(f"\n  Transactions: {data['count']}")
        if data['date_range']['min'] and data['date_range']['max']:
            print(f"  Date Range: {data['date_range']['min'].strftime('%Y-%m-%d')} to {data['date_range']['max'].strftime('%Y-%m-%d')}")
        print(f"  Total Charges: ${data['total_charges']:,.2f}")
        print(f"  Total Credits: ${data['total_credits']:,.2f}")
        print(f"  Net Spending: ${data['net']:,.2f}")

        # Top categories
        print(f"\n  Top Categories by Spending:")
        sorted_cats = sorted(data['categories'].items(), key=lambda x: x[1]['charges'], reverse=True)
        for cat, vals in sorted_cats[:5]:
            print(f"    {cat}: ${vals['charges']:,.2f} ({vals['count']} txn)")

        # Top subcategories
        print(f"\n  Top Sub-Categories by Spending:")
        sorted_subcats = sorted(data['subcategories'].items(), key=lambda x: x[1]['charges'], reverse=True)
        for subcat, vals in sorted_subcats[:8]:
            print(f"    {subcat}: ${vals['charges']:,.2f} ({vals['count']} txn)")

        # Monthly breakdown
        print(f"\n  Monthly Breakdown:")
        sorted_months = sorted(data['monthly'].keys())
        for year, month in sorted_months:
            month_name = datetime(year, month, 1).strftime("%b %Y")
            vals = data['monthly'][(year, month)]
            net = vals['charges'] - vals['credits']
            print(f"    {month_name}: ${vals['charges']:,.2f} charges, ${vals['credits']:,.2f} credits = ${net:,.2f} net ({vals['count']} txn)")

        # Aggregate into combined
        for cat, vals in data['categories'].items():
            combined_categories[cat]['charges'] += vals['charges']
            combined_categories[cat]['credits'] += vals['credits']
            combined_categories[cat]['count'] += vals['count']

        for subcat, vals in data['subcategories'].items():
            combined_subcategories[subcat]['charges'] += vals['charges']
            combined_subcategories[subcat]['credits'] += vals['credits']
            combined_subcategories[subcat]['count'] += vals['count']

        for month_key, vals in data['monthly'].items():
            combined_monthly[month_key]['charges'] += vals['charges']
            combined_monthly[month_key]['credits'] += vals['credits']
            combined_monthly[month_key]['count'] += vals['count']

        grand_charges += data['total_charges']
        grand_credits += data['total_credits']
        grand_count += data['count']

        if data['date_range']['min']:
            if overall_date_range['min'] is None or data['date_range']['min'] < overall_date_range['min']:
                overall_date_range['min'] = data['date_range']['min']
        if data['date_range']['max']:
            if overall_date_range['max'] is None or data['date_range']['max'] > overall_date_range['max']:
                overall_date_range['max'] = data['date_range']['max']

    # Combined summary
    print(f"\n{'='*80}")
    print("📊 COMBINED SUMMARY (ALL YEARS)")
    print("=" * 80)

    print(f"\n  Files Analyzed: {len(files)}")
    print(f"  Total Transactions: {grand_count}")
    if overall_date_range['min'] and overall_date_range['max']:
        print(f"  Date Range: {overall_date_range['min'].strftime('%Y-%m-%d')} to {overall_date_range['max'].strftime('%Y-%m-%d')}")
    print(f"\n  💰 Financial Summary:")
    print(f"     Total Charges: ${grand_charges:,.2f}")
    print(f"     Total Credits: ${grand_credits:,.2f}")
    print(f"     Net Spending:  ${grand_charges - grand_credits:,.2f}")

    print(f"\n  📁 Category Breakdown:")
    sorted_cats = sorted(combined_categories.items(), key=lambda x: x[1]['charges'], reverse=True)
    for cat, vals in sorted_cats:
        pct = (vals['charges'] / grand_charges * 100) if grand_charges else 0
        print(f"     {cat}: ${vals['charges']:,.2f} ({pct:.1f}%) - {vals['count']} transactions")

    print(f"\n  🏷️  Top 15 Sub-Categories:")
    sorted_subcats = sorted(combined_subcategories.items(), key=lambda x: x[1]['charges'], reverse=True)
    for subcat, vals in sorted_subcats[:15]:
        pct = (vals['charges'] / grand_charges * 100) if grand_charges else 0
        print(f"     {subcat}: ${vals['charges']:,.2f} ({pct:.1f}%) - {vals['count']} txn")

    # Monthly trend
    print(f"\n  📅 Monthly Spending Trend:")
    sorted_months = sorted(combined_monthly.keys())
    for year, month in sorted_months:
        month_name = datetime(year, month, 1).strftime("%b %Y")
        vals = combined_monthly[(year, month)]
        net = vals['charges'] - vals['credits']
        bar = "█" * int(vals['charges'] / 200)  # Simple bar chart
        print(f"     {month_name}: ${net:>8,.2f} ({vals['count']:>3} txn) {bar}")

if __name__ == "__main__":
    main()
