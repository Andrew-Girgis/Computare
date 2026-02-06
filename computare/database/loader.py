"""
Database loader for Computare.

Loads extracted JSON data into Supabase PostgreSQL database.
Populates raw_data JSONB for AI agent access.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

try:
    from supabase import create_client, Client
except ImportError:
    print("Warning: supabase-py not installed. Run: pip install supabase")
    create_client = None
    Client = None


@dataclass
class AccountMapping:
    """Maps source data to database account."""
    institution: str
    account_type: str
    name: str
    account_number_masked: Optional[str] = None


ACCOUNT_MAPPINGS = {
    'scotiabank_chequing': AccountMapping(
        institution='Scotiabank',
        account_type='chequing',
        name='Scotiabank Chequing',
        account_number_masked='****5080'
    ),
    'scotiabank_credit_card': AccountMapping(
        institution='Scotiabank',
        account_type='credit_card',
        name='Scotiabank Credit Card'
    ),
    'scotiabank_investments': AccountMapping(
        institution='Scotiabank',
        account_type='non_registered',
        name='Scotiabank iTRADE'
    ),
    'wealthsimple_tfsa': AccountMapping(
        institution='Wealthsimple',
        account_type='tfsa',
        name='Wealthsimple TFSA'
    ),
    'wealthsimple_activities': AccountMapping(
        institution='Wealthsimple',
        account_type='non_registered',
        name='Wealthsimple Personal'
    ),
    'wealthsimple_spending': AccountMapping(
        institution='Wealthsimple',
        account_type='spending',
        name='Wealthsimple Cash'
    ),
    'wealthsimple_credit_card': AccountMapping(
        institution='Wealthsimple',
        account_type='credit_card',
        name='Wealthsimple Credit Card'
    ),
    'wealthsimple_crypto': AccountMapping(
        institution='Wealthsimple',
        account_type='crypto',
        name='Wealthsimple Crypto'
    ),
    'american_express': AccountMapping(
        institution='American Express',
        account_type='credit_card',
        name='American Express',
        account_number_masked='****51001'
    ),
}

BATCH_SIZE = 100


class DatabaseLoader:
    """Load financial data into Supabase database."""

    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.url = supabase_url or os.environ.get('SUPABASE_URL')
        self.key = supabase_key or os.environ.get('SUPABASE_KEY')
        self.client: Optional[Client] = None
        self._institution_ids: Dict[str, str] = {}
        self._account_ids: Dict[str, str] = {}
        self._merchant_cache_entries: Dict[str, Dict] = {}  # raw_store -> cache entry

    def connect(self) -> bool:
        """Connect to Supabase."""
        if not self.url or not self.key:
            print("Error: SUPABASE_URL and SUPABASE_KEY must be set")
            return False
        if create_client is None:
            print("Error: supabase-py not installed")
            return False
        try:
            self.client = create_client(self.url, self.key)
            return True
        except Exception as e:
            print(f"Error connecting to Supabase: {e}")
            return False

    def _insert_batch(self, table: str, rows: List[dict]) -> List[dict]:
        """Insert rows in batches, returning all inserted records."""
        all_results = []
        for i in range(0, len(rows), BATCH_SIZE):
            chunk = rows[i:i + BATCH_SIZE]
            result = self.client.table(table).insert(chunk).execute()
            if result.data:
                all_results.extend(result.data)
        return all_results

    def setup_institutions_and_accounts(self) -> bool:
        """Create institutions and accounts from mappings."""
        if not self.client:
            return False

        institutions = set(m.institution for m in ACCOUNT_MAPPINGS.values())

        for name in institutions:
            try:
                result = self.client.table('institutions').upsert(
                    {'name': name}, on_conflict='name'
                ).execute()
                if result.data:
                    self._institution_ids[name] = result.data[0]['id']
            except Exception as e:
                print(f"Error inserting institution {name}: {e}")
                return False

        for key, mapping in ACCOUNT_MAPPINGS.items():
            inst_id = self._institution_ids.get(mapping.institution)
            if not inst_id:
                continue
            try:
                data = {
                    'institution_id': inst_id,
                    'account_type': mapping.account_type,
                    'name': mapping.name,
                    'account_number_masked': mapping.account_number_masked,
                    'currency': 'CAD',
                    'is_active': True
                }
                result = self.client.table('accounts').upsert(
                    data, on_conflict='institution_id,account_type,account_number_masked'
                ).execute()
                if result.data:
                    self._account_ids[key] = result.data[0]['id']
            except Exception as e:
                print(f"Error inserting account {mapping.name}: {e}")
                return False

        print(f"Created {len(self._institution_ids)} institutions and {len(self._account_ids)} accounts")
        return True

    def load_scotiabank_chequing(self, output_dir: Path) -> int:
        """Load Scotiabank chequing transactions."""
        account_id = self._account_ids.get('scotiabank_chequing')
        if not account_id:
            print("Error: Scotiabank chequing account not found")
            return 0

        skip_files = {'all_transactions.json', 'all_statements_analysis.json',
                      'discrepancies.json', 'financial_summary.json'}

        rows = []
        statement_rows = []

        for json_file in sorted(output_dir.glob('*.json')):
            if json_file.name in skip_files:
                continue
            try:
                with open(json_file) as f:
                    data = json.load(f)

                if 'transactions' not in data:
                    continue

                source_file = data.get('file', json_file.name)

                # Build statement record
                if data.get('year') and data.get('month'):
                    statement_rows.append({
                        'account_id': account_id,
                        'file_name': json_file.name,
                        'year': data['year'],
                        'month': data['month'],
                        'opening_balance': float(data['opening_balance']) if data.get('opening_balance') else None,
                        'closing_balance': float(data['closing_balance']) if data.get('closing_balance') else None,
                        'total_debits': float(data['total_debits']) if data.get('total_debits') else None,
                        'total_credits': float(data['total_credits']) if data.get('total_credits') else None,
                        'transaction_count': data.get('transaction_count'),
                        'confidence': float(data['confidence']) if data.get('confidence') else None,
                    })

                for t in data['transactions']:
                    # Use enriched merchant if available, otherwise fall back to raw store
                    raw_store = t.get('store', '')
                    merchant = t.get('merchant') or raw_store

                    rows.append({
                        'account_id': account_id,
                        'date': t['date'],
                        'description': t['description'],
                        'amount': float(t['amount']),
                        'balance': float(t['balance']) if t.get('balance') is not None else None,
                        'transaction_type': t.get('transaction_type', 'debit' if t['amount'] < 0 else 'credit'),
                        'merchant': merchant,
                        'location': t.get('location'),
                        'category': t.get('category'),
                        'sub_category': t.get('sub_category'),
                        'source_file': source_file,
                        'raw_text': t.get('raw_text'),
                        'raw_data': json.dumps({
                            'store': raw_store,
                            'merchant': merchant,
                            'location': t.get('location'),
                            'raw_text': t.get('raw_text'),
                            'description': t.get('description'),
                        }),
                    })

                    # Collect merchant cache entries from enriched data
                    if raw_store and merchant and t.get('category'):
                        self._merchant_cache_entries[raw_store] = {
                            'raw_store': raw_store,
                            'normalized_merchant': merchant,
                            'category': t['category'],
                            'sub_category': t.get('sub_category'),
                            'source': 'json',
                        }

            except Exception as e:
                print(f"  Error loading {json_file.name}: {e}")

        if statement_rows:
            self._insert_batch('statements', statement_rows)

        if rows:
            self._insert_batch('transactions', rows)

        return len(rows)

    def load_scotiabank_credit_card(self, credit_card_dir: Path) -> int:
        """Load Scotiabank credit card transactions."""
        account_id = self._account_ids.get('scotiabank_credit_card')
        if not account_id:
            print("Error: Scotiabank credit card account not found")
            return 0

        rows = []
        for json_file in sorted(credit_card_dir.glob('*.json')):
            try:
                with open(json_file) as f:
                    data = json.load(f)

                source_file = data.get('metadata', {}).get('source_file', json_file.name)

                for t in data.get('transactions', []):
                    # Use enriched merchant if available, otherwise use description
                    raw_desc = t.get('description', '')
                    merchant = t.get('merchant') or raw_desc

                    rows.append({
                        'account_id': account_id,
                        'date': t['date'],
                        'description': raw_desc,
                        'amount': float(t['amount']),
                        'balance': None,
                        'transaction_type': t.get('type', 'debit' if t['amount'] < 0 else 'credit'),
                        'merchant': merchant,
                        'category': t.get('category'),
                        'sub_category': t.get('sub_category'),
                        'source_file': source_file,
                        'raw_text': t.get('raw_text'),
                        'raw_data': json.dumps({
                            'raw_text': t.get('raw_text'),
                            'description': raw_desc,
                            'merchant': merchant,
                        }),
                    })

                    # Collect merchant cache entries from enriched data
                    if raw_desc and merchant and t.get('category'):
                        self._merchant_cache_entries[raw_desc] = {
                            'raw_store': raw_desc,
                            'normalized_merchant': merchant,
                            'category': t['category'],
                            'sub_category': t.get('sub_category'),
                            'source': 'json',
                        }

            except Exception as e:
                print(f"  Error loading {json_file.name}: {e}")

        if rows:
            self._insert_batch('transactions', rows)

        return len(rows)

    def load_scotiabank_investments(self, investments_dir: Path) -> int:
        """Load Scotiabank iTRADE investment transactions."""
        account_id = self._account_ids.get('scotiabank_investments')
        if not account_id:
            print("Error: Scotiabank investments account not found")
            return 0

        rows = []
        trade_rows = []

        for json_file in sorted(investments_dir.glob('*.json')):
            try:
                with open(json_file) as f:
                    data = json.load(f)

                source_file = data.get('metadata', {}).get('source_file', json_file.name)

                for t in data.get('transactions', []):
                    # Parse activity type from description (e.g. "BUY AIRCANADA" → "BUY")
                    desc = t.get('description', '')
                    activity = None
                    for act in ['BUY', 'SELL', 'DIV', 'FEE', 'CONT', 'WITHDRAW']:
                        if desc.upper().startswith(act):
                            activity = act
                            break

                    # Parse symbol and quantity from description
                    symbol = None
                    quantity = None
                    unit_price = None
                    import re
                    # Pattern: "BUY AIRCANADA (25.0 @ $8.76)" or "SELL URANIUMROYALTYCORP"
                    match = re.search(r'(?:BUY|SELL)\s+(\S+)\s*\((-?[\d.]+)\s*@\s*\$?([\d.]+)\)', desc)
                    if match:
                        symbol = match.group(1)
                        quantity = float(match.group(2))
                        unit_price = float(match.group(3))
                    else:
                        # Try just symbol after action
                        match = re.search(r'(?:BUY|SELL)\s+(\S+)', desc)
                        if match:
                            symbol = match.group(1)

                    # Use enriched fields if available
                    merchant = t.get('merchant') or desc

                    row = {
                        'account_id': account_id,
                        'date': t['date'],
                        'description': desc,
                        'amount': float(t['amount']),
                        'balance': None,
                        'transaction_type': t.get('type', 'debit' if t['amount'] < 0 else 'credit'),
                        'activity_type': activity,
                        'merchant': merchant,
                        'category': t.get('category'),
                        'sub_category': t.get('sub_category'),
                        'source_file': source_file,
                        'raw_text': t.get('raw_text'),
                        'raw_data': json.dumps({
                            'raw_text': t.get('raw_text'),
                            'description': desc,
                            'symbol': symbol,
                            'quantity': quantity,
                            'unit_price': unit_price,
                        }),
                    }

                    # Collect merchant cache entries from enriched data
                    if desc and merchant and t.get('category'):
                        self._merchant_cache_entries[desc] = {
                            'raw_store': desc,
                            'normalized_merchant': merchant,
                            'category': t['category'],
                            'sub_category': t.get('sub_category'),
                            'source': 'json',
                        }
                    rows.append(row)

                    # Track trade details to insert after transactions
                    if symbol:
                        trade_rows.append({
                            '_row_index': len(rows) - 1,
                            'symbol': symbol,
                            'quantity': quantity,
                            'unit_price': unit_price,
                            'currency': 'CAD',
                        })

            except Exception as e:
                print(f"  Error loading {json_file.name}: {e}")

        if rows:
            results = self._insert_batch('transactions', rows)

            # Insert trade details linking to transaction IDs
            if trade_rows and results:
                trade_inserts = []
                for tr in trade_rows:
                    idx = tr['_row_index']
                    if idx < len(results):
                        trade_inserts.append({
                            'transaction_id': results[idx]['id'],
                            'symbol': tr['symbol'],
                            'quantity': tr['quantity'],
                            'unit_price': tr['unit_price'],
                            'currency': tr['currency'],
                        })
                if trade_inserts:
                    self._insert_batch('trade_details', trade_inserts)

        return len(rows)

    def load_wealthsimple(self, wealthsimple_dir: Path) -> Dict[str, int]:
        """Load Wealthsimple data from JSON files."""
        counts = {}

        account_type_map = {
            'investments': 'wealthsimple_tfsa',
            'activities': 'wealthsimple_activities',
            'spending': 'wealthsimple_spending',
            'credit_card': 'wealthsimple_credit_card',
            'crypto': 'wealthsimple_crypto',
        }

        for ws_type, account_key in account_type_map.items():
            json_file = wealthsimple_dir / f'{ws_type}.json'
            if not json_file.exists():
                counts[ws_type] = 0
                continue

            account_id = self._account_ids.get(account_key)
            if not account_id:
                print(f"  Warning: {account_key} account not found, skipping")
                counts[ws_type] = 0
                continue

            try:
                with open(json_file) as f:
                    data = json.load(f)

                rows = []
                trade_indices = []

                for t in data.get('transactions', []):
                    trans_type = 'credit' if t['amount'] > 0 else 'debit'
                    activity = t.get('transaction_type')

                    # Normalize activity types
                    if activity and activity.startswith('Trade_'):
                        activity = activity.replace('Trade_', '')

                    raw_data = {
                        'transaction_type': t.get('transaction_type'),
                        'currency': t.get('currency'),
                        'symbol': t.get('symbol'),
                        'quantity': t.get('quantity'),
                        'unit_price': t.get('unit_price'),
                    }

                    # Extract FX rate from description if present
                    desc = t.get('description', '')
                    import re
                    fx_match = re.search(r'FX Rate:\s*([\d.]+)', desc)
                    if fx_match:
                        raw_data['fx_rate'] = float(fx_match.group(1))

                    # Use enriched merchant if available
                    merchant = t.get('merchant') or desc

                    row = {
                        'account_id': account_id,
                        'date': t['date'],
                        'description': desc,
                        'amount': float(t['amount']),
                        'balance': float(t['balance']) if t.get('balance') is not None else None,
                        'transaction_type': trans_type,
                        'activity_type': activity,
                        'merchant': merchant,
                        'category': t.get('category'),
                        'sub_category': t.get('sub_category'),
                        'source_file': f'wealthsimple/{ws_type}.json',
                        'raw_data': json.dumps(raw_data),
                    }
                    rows.append(row)

                    # Collect merchant cache entries from enriched data
                    if desc and merchant and t.get('category'):
                        self._merchant_cache_entries[desc] = {
                            'raw_store': desc,
                            'normalized_merchant': merchant,
                            'category': t['category'],
                            'sub_category': t.get('sub_category'),
                            'source': 'json',
                        }

                    if t.get('symbol'):
                        trade_indices.append({
                            '_row_index': len(rows) - 1,
                            'symbol': t['symbol'],
                            'quantity': float(t['quantity']) if t.get('quantity') else None,
                            'unit_price': float(t['unit_price']) if t.get('unit_price') else None,
                            'currency': t.get('currency', 'CAD'),
                            'fx_rate': raw_data.get('fx_rate'),
                        })

                if rows:
                    results = self._insert_batch('transactions', rows)

                    if trade_indices and results:
                        trade_inserts = []
                        for tr in trade_indices:
                            idx = tr['_row_index']
                            if idx < len(results):
                                trade_inserts.append({
                                    'transaction_id': results[idx]['id'],
                                    'symbol': tr['symbol'],
                                    'quantity': tr['quantity'],
                                    'unit_price': tr['unit_price'],
                                    'currency': tr['currency'],
                                    'fx_rate': tr.get('fx_rate'),
                                })
                        if trade_inserts:
                            self._insert_batch('trade_details', trade_inserts)

                counts[ws_type] = len(rows)

            except Exception as e:
                print(f"  Error loading {json_file.name}: {e}")
                counts[ws_type] = 0

        return counts

    def load_american_express(self, amex_dir: Path) -> int:
        """Load American Express data from JSON files."""
        account_id = self._account_ids.get('american_express')
        if not account_id:
            print("Error: American Express account not found")
            return 0

        rows = []
        for json_file in sorted(amex_dir.glob('*.json')):
            try:
                with open(json_file) as f:
                    data = json.load(f)

                source_file = data.get('source', json_file.name)

                for t in data.get('transactions', []):
                    date_str = t.get('Date', '')
                    try:
                        trans_date = datetime.strptime(date_str, '%d/%m/%Y').date().isoformat()
                    except ValueError:
                        continue

                    charges_str = t.get('Charges $', '').replace(',', '').strip()
                    credits_str = t.get('Credits $', '').replace(',', '').strip()

                    if charges_str:
                        amount = -float(charges_str)
                        trans_type = 'debit'
                    elif credits_str:
                        amount = float(credits_str)
                        trans_type = 'credit'
                    else:
                        continue

                    rows.append({
                        'account_id': account_id,
                        'date': trans_date,
                        'description': t.get('Transaction', ''),
                        'amount': amount,
                        'balance': None,
                        'transaction_type': trans_type,
                        'category': t.get('Category'),
                        'sub_category': t.get('Sub-Category'),
                        'source_file': source_file,
                        'raw_data': json.dumps({
                            'category': t.get('Category'),
                            'sub_category': t.get('Sub-Category'),
                            'card_member': t.get('Card Member'),
                            'account_number': t.get('Account Number'),
                            'month_billed': t.get('Month-Billed'),
                        }),
                    })

            except Exception as e:
                print(f"  Error loading {json_file.name}: {e}")

        if rows:
            self._insert_batch('transactions', rows)

        return len(rows)

    def save_merchant_cache(self) -> int:
        """Save collected merchant cache entries to database."""
        if not self.client or not self._merchant_cache_entries:
            return 0

        print(f"\nSaving {len(self._merchant_cache_entries)} merchant cache entries...")
        rows = list(self._merchant_cache_entries.values())

        # Upsert to handle duplicates
        try:
            for i in range(0, len(rows), BATCH_SIZE):
                chunk = rows[i:i + BATCH_SIZE]
                self.client.table('merchant_cache').upsert(
                    chunk, on_conflict='raw_store'
                ).execute()
            print(f"  Merchant cache populated.")
            return len(rows)
        except Exception as e:
            print(f"  Error saving merchant cache: {e}")
            return 0

    def refresh_summaries(self):
        """Refresh all materialized views after loading data."""
        if not self.client:
            return
        print("\nRefreshing materialized views...")
        try:
            self.client.rpc('refresh_all_summaries').execute()
            print("  All summaries refreshed.")
        except Exception as e:
            print(f"  Error refreshing summaries: {e}")
            print("  Trying individual refreshes...")
            views = [
                'monthly_spending_by_category', 'monthly_spending_by_account',
                'yearly_summary', 'net_worth_timeline', 'merchant_summary',
                'category_trends', 'investment_activity', 'current_holdings',
                'transfer_summary',
            ]
            for view in views:
                try:
                    self.client.postgrest.schema('public')
                    self.client.rpc('', params={}).execute()
                except Exception:
                    pass
            # Fallback: direct SQL via psql if RPC fails
            import subprocess
            try:
                subprocess.run([
                    'psql', '-h', '127.0.0.1', '-p', '54322',
                    '-U', 'postgres', '-d', 'postgres',
                    '-c', 'SELECT refresh_all_summaries();'
                ], env={**os.environ, 'PGPASSWORD': os.environ.get('PGPASSWORD', 'postgres')},
                    capture_output=True, text=True)
                print("  Summaries refreshed via psql fallback.")
            except Exception as e2:
                print(f"  Fallback also failed: {e2}")

    def load_all(self, output_dir: str | Path) -> Dict[str, int]:
        """Load all financial data from the output directory."""
        output_dir = Path(output_dir)
        results = {}

        if not self.connect():
            return results

        print("Setting up institutions and accounts...")
        if not self.setup_institutions_and_accounts():
            return results

        # Scotiabank Chequing
        print("\nLoading Scotiabank Chequing...")
        results['scotiabank_chequing'] = self.load_scotiabank_chequing(output_dir)
        print(f"  {results['scotiabank_chequing']} transactions")

        # Scotiabank Credit Card
        credit_card_dir = output_dir / 'credit_card'
        if credit_card_dir.exists():
            print("\nLoading Scotiabank Credit Card...")
            results['scotiabank_credit_card'] = self.load_scotiabank_credit_card(credit_card_dir)
            print(f"  {results['scotiabank_credit_card']} transactions")

        # Scotiabank Investments
        investments_dir = output_dir / 'investments'
        if investments_dir.exists():
            print("\nLoading Scotiabank Investments...")
            results['scotiabank_investments'] = self.load_scotiabank_investments(investments_dir)
            print(f"  {results['scotiabank_investments']} transactions")

        # Wealthsimple
        wealthsimple_dir = output_dir / 'wealthsimple'
        if wealthsimple_dir.exists():
            print("\nLoading Wealthsimple...")
            ws_counts = self.load_wealthsimple(wealthsimple_dir)
            for k, v in ws_counts.items():
                results[f'wealthsimple_{k}'] = v
                if v > 0:
                    print(f"  {k}: {v} transactions")

        # American Express
        amex_dir = output_dir / 'amex'
        if amex_dir.exists():
            print("\nLoading American Express...")
            results['american_express'] = self.load_american_express(amex_dir)
            print(f"  {results['american_express']} transactions")

        total = sum(results.values())
        print(f"\n{'='*40}")
        print(f"Total: {total} transactions loaded")
        print(f"{'='*40}")

        # Save merchant cache from enriched JSON data
        cache_count = self.save_merchant_cache()
        if cache_count:
            results['merchant_cache'] = cache_count

        # Refresh materialized views
        self.refresh_summaries()

        return results


def main():
    """CLI entry point for loading data."""
    from dotenv import load_dotenv
    load_dotenv()

    import argparse

    parser = argparse.ArgumentParser(description='Load financial data into Supabase')
    parser.add_argument('output_dir', help='Path to output directory with JSON files')
    parser.add_argument('--url', help='Supabase URL (or set SUPABASE_URL env var)')
    parser.add_argument('--key', help='Supabase service key (or set SUPABASE_KEY env var)')

    args = parser.parse_args()

    loader = DatabaseLoader(args.url, args.key)
    results = loader.load_all(args.output_dir)

    if results:
        print("\nLoad complete!")
        for source, count in sorted(results.items()):
            print(f"  {source}: {count}")


if __name__ == '__main__':
    main()
