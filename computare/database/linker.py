"""
Transaction linker for Computare.

Detects and links transfer transactions between accounts.
For example: Scotiabank Chequing -> Wealthsimple TFSA contribution
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from supabase import create_client, Client
except ImportError:
    print("Warning: supabase-py not installed. Run: pip install supabase")
    create_client = None
    Client = None


@dataclass
class TransferCandidate:
    """A potential transfer between accounts."""
    outflow_id: str
    outflow_account: str
    outflow_date: str
    outflow_amount: float
    outflow_description: str
    inflow_id: str
    inflow_account: str
    inflow_date: str
    inflow_amount: float
    inflow_description: str
    confidence: float  # 0-1 score


class TransactionLinker:
    """Detect and link transfer transactions between accounts."""

    # Known transfer patterns
    TRANSFER_PATTERNS = {
        # Scotiabank chequing -> Wealthsimple patterns
        'wealthsimple_contrib': {
            'outflow_keywords': ['wealthsimple', 'ws transfer', 'tfr wealthsimple'],
            'inflow_keywords': ['contribution', 'cont', 'deposit', 'trfin'],
        },
        # Credit card payment patterns
        'cc_payment': {
            'outflow_keywords': ['creditcard', 'credit card', 'loc payment', 'visa payment'],
            'inflow_keywords': ['payment from', 'payment received', 'payment'],
        },
        # Internal transfer patterns
        'internal_transfer': {
            'outflow_keywords': ['transfer to', 'mb-transfer', 'tfr to'],
            'inflow_keywords': ['transfer from', 'mb-transfer', 'tfr from'],
        },
        # E-transfer patterns
        'etransfer': {
            'outflow_keywords': ['interac e-transfer', 'email money', 'e-transfer sent'],
            'inflow_keywords': ['interac e-transfer', 'email money', 'e-transfer'],
        },
    }

    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """
        Initialize transaction linker.

        Args:
            supabase_url: Supabase project URL (or set SUPABASE_URL env var)
            supabase_key: Supabase service key (or set SUPABASE_KEY env var)
        """
        self.url = supabase_url or os.environ.get('SUPABASE_URL')
        self.key = supabase_key or os.environ.get('SUPABASE_KEY')
        self.client: Optional[Client] = None

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

    def find_transfer_candidates(
        self,
        date_tolerance_days: int = 3,
        amount_tolerance: float = 0.01
    ) -> List[TransferCandidate]:
        """
        Find potential transfer pairs between accounts.

        Args:
            date_tolerance_days: Max days difference between outflow and inflow
            amount_tolerance: Max amount difference (for rounding/fees)

        Returns:
            List of TransferCandidate objects
        """
        if not self.client:
            if not self.connect():
                return []

        candidates = []

        # Get all unlinked outflows (negative amounts)
        outflows_result = self.client.table('transactions').select(
            'id, account_id, date, amount, description, accounts!inner(name, account_type)'
        ).lt('amount', 0).is_('linked_transaction_id', 'null').execute()

        # Get all unlinked inflows (positive amounts)
        inflows_result = self.client.table('transactions').select(
            'id, account_id, date, amount, description, accounts!inner(name, account_type)'
        ).gt('amount', 0).is_('linked_transaction_id', 'null').execute()

        outflows = outflows_result.data or []
        inflows = inflows_result.data or []

        print(f"Analyzing {len(outflows)} outflows and {len(inflows)} inflows...")

        for outflow in outflows:
            outflow_amount = abs(outflow['amount'])
            outflow_date = datetime.strptime(outflow['date'], '%Y-%m-%d')
            outflow_account = outflow['accounts']['name']
            outflow_desc = outflow['description'].lower()

            for inflow in inflows:
                # Skip if same account
                if outflow['account_id'] == inflow['account_id']:
                    continue

                inflow_amount = inflow['amount']
                inflow_date = datetime.strptime(inflow['date'], '%Y-%m-%d')
                inflow_account = inflow['accounts']['name']
                inflow_desc = inflow['description'].lower()

                # Check amount match
                amount_diff = abs(outflow_amount - inflow_amount)
                if amount_diff > amount_tolerance * outflow_amount and amount_diff > 1.0:
                    continue

                # Check date proximity
                date_diff = abs((inflow_date - outflow_date).days)
                if date_diff > date_tolerance_days:
                    continue

                # Calculate confidence score
                confidence = self._calculate_confidence(
                    outflow_desc, inflow_desc,
                    outflow_account, inflow_account,
                    amount_diff, date_diff
                )

                if confidence > 0.3:  # Minimum threshold
                    candidates.append(TransferCandidate(
                        outflow_id=outflow['id'],
                        outflow_account=outflow_account,
                        outflow_date=outflow['date'],
                        outflow_amount=outflow['amount'],
                        outflow_description=outflow['description'],
                        inflow_id=inflow['id'],
                        inflow_account=inflow_account,
                        inflow_date=inflow['date'],
                        inflow_amount=inflow['amount'],
                        inflow_description=inflow['description'],
                        confidence=confidence
                    ))

        # Sort by confidence (highest first)
        candidates.sort(key=lambda x: x.confidence, reverse=True)

        return candidates

    def _calculate_confidence(
        self,
        outflow_desc: str,
        inflow_desc: str,
        outflow_account: str,
        inflow_account: str,
        amount_diff: float,
        date_diff: int
    ) -> float:
        """Calculate confidence score for a transfer match."""
        score = 0.0

        # Exact amount match: +0.3
        if amount_diff < 0.01:
            score += 0.3
        elif amount_diff < 1.0:
            score += 0.2

        # Same date: +0.2, within 1 day: +0.1
        if date_diff == 0:
            score += 0.2
        elif date_diff == 1:
            score += 0.1

        # Check known transfer patterns
        for pattern_name, patterns in self.TRANSFER_PATTERNS.items():
            outflow_match = any(kw in outflow_desc for kw in patterns['outflow_keywords'])
            inflow_match = any(kw in inflow_desc for kw in patterns['inflow_keywords'])

            if outflow_match and inflow_match:
                score += 0.4
                break
            elif outflow_match or inflow_match:
                score += 0.15

        # Account type matching logic
        # Chequing -> Investment account is common
        if 'chequing' in outflow_account.lower():
            if any(x in inflow_account.lower() for x in ['tfsa', 'rrsp', 'investment']):
                score += 0.1

        # Credit card payment logic
        if 'credit' in inflow_account.lower() and 'payment' in inflow_desc:
            score += 0.1

        return min(score, 1.0)

    def link_transactions(self, outflow_id: str, inflow_id: str) -> bool:
        """
        Link two transactions as a transfer.

        Args:
            outflow_id: ID of the outflow transaction
            inflow_id: ID of the inflow transaction

        Returns:
            True if linking succeeded
        """
        if not self.client:
            return False

        try:
            # Update outflow to point to inflow
            self.client.table('transactions').update({
                'linked_transaction_id': inflow_id
            }).eq('id', outflow_id).execute()

            # Update inflow to point to outflow
            self.client.table('transactions').update({
                'linked_transaction_id': outflow_id
            }).eq('id', inflow_id).execute()

            return True
        except Exception as e:
            print(f"Error linking transactions: {e}")
            return False

    def auto_link_high_confidence(self, min_confidence: float = 0.7) -> int:
        """
        Automatically link high-confidence transfer candidates.

        Args:
            min_confidence: Minimum confidence threshold (0-1)

        Returns:
            Number of transfers linked
        """
        candidates = self.find_transfer_candidates()
        linked_count = 0
        linked_ids = set()  # Track already linked transactions

        for candidate in candidates:
            if candidate.confidence < min_confidence:
                continue

            # Skip if either transaction is already linked in this session
            if candidate.outflow_id in linked_ids or candidate.inflow_id in linked_ids:
                continue

            if self.link_transactions(candidate.outflow_id, candidate.inflow_id):
                linked_ids.add(candidate.outflow_id)
                linked_ids.add(candidate.inflow_id)
                linked_count += 1
                print(f"Linked: {candidate.outflow_account} -> {candidate.inflow_account} "
                      f"${abs(candidate.outflow_amount):.2f} ({candidate.confidence:.0%} confidence)")

        return linked_count

    def review_candidates(self, min_confidence: float = 0.3) -> None:
        """
        Print transfer candidates for manual review.

        Args:
            min_confidence: Minimum confidence to show
        """
        candidates = self.find_transfer_candidates()

        print(f"\n{'='*80}")
        print("TRANSFER CANDIDATES FOR REVIEW")
        print(f"{'='*80}\n")

        for i, c in enumerate(candidates, 1):
            if c.confidence < min_confidence:
                continue

            print(f"#{i} - Confidence: {c.confidence:.0%}")
            print(f"  OUT: {c.outflow_date} | {c.outflow_account}")
            print(f"       {c.outflow_description[:60]}")
            print(f"       Amount: ${abs(c.outflow_amount):.2f}")
            print(f"  IN:  {c.inflow_date} | {c.inflow_account}")
            print(f"       {c.inflow_description[:60]}")
            print(f"       Amount: ${c.inflow_amount:.2f}")
            print()


def main():
    """CLI entry point for linking transactions."""
    import argparse

    parser = argparse.ArgumentParser(description='Link transfer transactions between accounts')
    parser.add_argument('--url', help='Supabase URL (or set SUPABASE_URL env var)')
    parser.add_argument('--key', help='Supabase service key (or set SUPABASE_KEY env var)')
    parser.add_argument('--auto', action='store_true', help='Auto-link high confidence transfers')
    parser.add_argument('--min-confidence', type=float, default=0.7,
                        help='Minimum confidence for auto-linking (default: 0.7)')
    parser.add_argument('--review', action='store_true', help='Review candidates without linking')

    args = parser.parse_args()

    linker = TransactionLinker(args.url, args.key)

    if not linker.connect():
        return

    if args.review:
        linker.review_candidates(min_confidence=0.3)
    elif args.auto:
        count = linker.auto_link_high_confidence(min_confidence=args.min_confidence)
        print(f"\nLinked {count} transfer pairs")
    else:
        # Default: show candidates
        linker.review_candidates(min_confidence=0.5)


if __name__ == '__main__':
    main()
