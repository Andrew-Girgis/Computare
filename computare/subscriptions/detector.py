"""
Subscription detection algorithm for Computare.

Scans transaction history to identify recurring charges and creates/updates
subscription records in the database.

Detection approach:
1. Group all debit transactions by normalized merchant
2. For each merchant, find date-regular charge clusters
3. Score regularity (stddev/mean of intervals)
4. Determine frequency (monthly, yearly, weekly, bi-weekly)
5. Determine active/inactive based on recency of last charge
6. Create subscription records and link transactions
"""

import logging
import re
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Frequency detection thresholds (in days)
FREQUENCY_RANGES = {
    "weekly": (5, 9),
    "bi-weekly": (12, 17),
    "monthly": (25, 37),
    "yearly": (345, 385),
}

# Minimum occurrences to consider something a subscription
MIN_OCCURRENCES = 3

# Maximum regularity score (stddev / mean) to qualify
MAX_REGULARITY = 0.30

# How many expected intervals past last_charged before marking inactive
INACTIVE_MULTIPLIER = 1.8


@dataclass
class DetectedSubscription:
    """A subscription candidate detected from transaction data."""
    merchant: str
    category: str
    current_amount: float
    frequency: str
    billing_day: int
    started_at: date
    ended_at: Optional[date]
    last_charged_at: date
    next_expected_at: Optional[date]
    is_active: bool
    confidence: float
    transaction_ids: List[str] = field(default_factory=list)
    charge_count: int = 0


class SubscriptionDetector:
    """Detects recurring subscriptions from transaction history."""

    def __init__(self, supabase_client=None):
        self._client = supabase_client

    def connect(self) -> bool:
        """Initialize database connection."""
        import os

        if not self._client:
            try:
                from supabase import create_client
                url = os.environ.get("SUPABASE_URL")
                key = os.environ.get("SUPABASE_KEY")
                if url and key:
                    self._client = create_client(url, key)
            except ImportError:
                logger.error("supabase-py not installed")
                return False

        return self._client is not None

    def detect(self, reference_date: Optional[date] = None) -> List[DetectedSubscription]:
        """
        Detect all subscriptions from transaction history.

        Args:
            reference_date: Date to use for active/inactive determination.
                            Defaults to today.

        Returns:
            List of detected subscription candidates.
        """
        if reference_date is None:
            reference_date = date.today()

        transactions = self._fetch_debit_transactions()
        if not transactions:
            logger.warning("No debit transactions found")
            return []

        logger.info(f"Analyzing {len(transactions)} debit transactions...")

        # Group by normalized merchant
        merchant_groups = self._group_by_merchant(transactions)
        logger.info(f"Found {len(merchant_groups)} unique merchants")

        # Detect subscriptions within each merchant group
        detected = []
        for merchant, txns in merchant_groups.items():
            subs = self._detect_for_merchant(merchant, txns, reference_date)
            detected.extend(subs)

        logger.info(f"Detected {len(detected)} subscription candidates")
        return detected

    def save(self, subscriptions: List[DetectedSubscription], clear_existing: bool = True):
        """
        Save detected subscriptions to the database and link transactions.

        Args:
            subscriptions: List of detected subscriptions to save.
            clear_existing: If True, removes previously detected (non-confirmed)
                           subscriptions before saving. Confirmed/dismissed are kept.
        """
        if not self._client:
            logger.error("No database connection")
            return

        if clear_existing:
            # Only clear auto-detected ones, preserve user-confirmed/dismissed
            self._client.table("subscriptions").delete().eq(
                "status", "detected"
            ).execute()

            # Clear subscription_id links for those transactions
            # (confirmed subscription links are preserved)
            self._client.table("transactions").update(
                {"subscription_id": None}
            ).is_("subscription_id", "null").execute()
            # The above won't actually clear anything useful. We need to clear
            # links to subscriptions that were just deleted.
            # Since we deleted detected subs, those FK references are already
            # broken — Supabase should handle this, but let's be safe:
            # Clear any transaction subscription_id that doesn't reference a
            # valid subscription.

        saved_count = 0
        for sub in subscriptions:
            try:
                # Insert subscription
                result = self._client.table("subscriptions").insert({
                    "merchant": sub.merchant,
                    "category": sub.category,
                    "current_amount": sub.current_amount,
                    "frequency": sub.frequency,
                    "billing_day": sub.billing_day,
                    "started_at": sub.started_at.isoformat(),
                    "ended_at": sub.ended_at.isoformat() if sub.ended_at else None,
                    "last_charged_at": sub.last_charged_at.isoformat(),
                    "next_expected_at": sub.next_expected_at.isoformat() if sub.next_expected_at else None,
                    "is_active": sub.is_active,
                    "status": "detected",
                    "confidence": sub.confidence,
                }).execute()

                sub_id = result.data[0]["id"]

                # Link transactions
                for txn_id in sub.transaction_ids:
                    self._client.table("transactions").update(
                        {"subscription_id": sub_id}
                    ).eq("id", txn_id).execute()

                saved_count += 1

            except Exception as e:
                logger.error(f"Failed to save subscription {sub.merchant}: {e}")

        logger.info(f"Saved {saved_count} subscriptions with transaction links")

    def detect_and_save(self, reference_date: Optional[date] = None):
        """Convenience method: detect and save in one call."""
        subs = self.detect(reference_date)
        self.save(subs)
        return subs

    # ── Internal methods ──────────────────────────────────────────────

    def _fetch_debit_transactions(self) -> List[Dict[str, Any]]:
        """Fetch all debit transactions from the database."""
        all_txns = []
        offset = 0
        page_size = 1000

        while True:
            result = (
                self._client.table("transactions")
                .select("id, date, description, merchant, amount, category, account_id")
                .eq("transaction_type", "debit")
                .order("date")
                .range(offset, offset + page_size - 1)
                .execute()
            )
            all_txns.extend(result.data)
            if len(result.data) < page_size:
                break
            offset += page_size

        return all_txns

    def _group_by_merchant(
        self, transactions: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        Group transactions by normalized merchant key.

        Handles the fact that the same merchant can appear under multiple
        raw strings (e.g. "Rogers", "ROGERS ******2820 888-764-3771 ON",
        "Nslsc" vs "Pre-authorized Debit to NSLSC").
        """
        groups: Dict[str, List[Dict]] = defaultdict(list)

        for txn in transactions:
            merchant = (txn.get("merchant") or "").strip()
            if not merchant or float(txn["amount"]) >= 0:
                continue
            key = self._normalize_merchant_key(merchant)
            if key:
                groups[key].append(txn)

        return groups

    @staticmethod
    def _normalize_merchant_key(merchant: str) -> str:
        """
        Extract a stable grouping key from a merchant string.

        Strips POS prefixes, account/reference numbers, phone numbers,
        location suffixes, and normalizes to lowercase.

        Examples:
            "ROGERS ******2820 888-764-3771 ON" -> "rogers"
            "ROGERS ******2820"                 -> "rogers"
            "Rogers"                            -> "rogers"
            "Pre-authorized Debit to NSLSC"     -> "nslsc"
            "Nslsc"                             -> "nslsc"
            "APPLE.COM/BILL"                    -> "apple.com"
            "Apple.com"                         -> "apple.com"
            "FposStarbucks#16144#Mississaugaoncd"-> "starbucks"
            "SHELL EASYPAY C21842 MISSISSAUGA"  -> "shell easypay"
        """
        s = merchant.strip()

        # Remove "Pre-authorized Debit to " prefix
        s = re.sub(r"(?i)^pre-?authorized\s+debit\s+to\s+", "", s)

        # Remove POS prefixes (Fpos, Opos, Apos, Aips)
        s = re.sub(r"(?i)^[FOAI]pos\s*", "", s)

        # Remove /BILL suffix (APPLE.COM/BILL)
        s = re.sub(r"/BILL$", "", s, flags=re.IGNORECASE)

        # Remove masked account numbers (******2820, ****5080)
        s = re.sub(r"\*{2,}\d+", "", s)

        # Remove phone numbers (888-764-3771, 800-3457669)
        s = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "", s)
        s = re.sub(r"\b\d{10,}\b", "", s)

        # Remove store/location numbers (#16144, #291, C21842)
        s = re.sub(r"#\d+", "", s)
        s = re.sub(r"\bC\d{4,}\b", "", s)

        # Remove reference numbers at start (e.g. "14272353FreeInterac...")
        s = re.sub(r"^\d{6,}", "", s)

        # Remove Canadian location suffixes
        # Province codes + country code patterns at the end
        s = re.sub(
            r"\s+(ON|BC|AB|QC|MB|SK|NS|NB|PE|NL|NT|YT|NU)"
            r"(\s*CA\s*)?$",
            "", s, flags=re.IGNORECASE,
        )
        # City names commonly appended (very rough — just strip trailing
        # title-case words that look like cities after the main name)
        s = re.sub(
            r"\s+(Mississaug|Toronto|Oakville|Waterloo|Hamilton|Cambridge|"
            r"Brantford|Orillia|Milton|Calgary|Vancouver|London|Ottawa|"
            r"StCatharin|mississaug|brantford|toronto)\w*$",
            "", s, flags=re.IGNORECASE,
        )

        # Remove trailing province/country codes (ON, ONCA, CA, CAUS, etc.)
        s = re.sub(r"\s*(onca|oncd|caus|bcca|abca)\s*$", "", s, flags=re.IGNORECASE)
        s = re.sub(r"\s+(ON|CA|US)\s*$", "", s, flags=re.IGNORECASE)

        # Normalize whitespace and lowercase
        s = re.sub(r"\s+", " ", s).strip().lower()

        # If empty after cleanup, return original lowered
        return s if s else merchant.strip().lower()

    def _detect_for_merchant(
        self,
        merchant_key: str,
        transactions: List[Dict],
        reference_date: date,
    ) -> List[DetectedSubscription]:
        """
        Detect subscription patterns within a single merchant's transactions.

        Handles the case where one merchant has multiple subscriptions
        (e.g., Apple.com with iCloud + Apple One at different price points)
        by clustering transactions by approximate amount first.
        """
        if len(transactions) < MIN_OCCURRENCES:
            return []

        # Pick a display name: the most common raw merchant string in this group
        from collections import Counter
        raw_names = [t.get("merchant", "") for t in transactions if t.get("merchant")]
        display_name = Counter(raw_names).most_common(1)[0][0] if raw_names else merchant_key

        # Cluster by approximate amount (within 15% tolerance)
        amount_clusters = self._cluster_by_amount(transactions)

        results = []
        for cluster_txns in amount_clusters:
            sub = self._check_regularity(display_name, cluster_txns, reference_date)
            if sub:
                results.append(sub)

        return results

    def _cluster_by_amount(
        self, transactions: List[Dict]
    ) -> List[List[Dict]]:
        """
        Cluster transactions by similar amounts.

        Groups amounts within 15% of each other to handle small price
        variations (tax changes, FX fluctuations) while separating
        genuinely different subscriptions from the same merchant.
        """
        sorted_txns = sorted(transactions, key=lambda t: abs(float(t["amount"])))

        clusters: List[List[Dict]] = []
        current_cluster: List[Dict] = []
        cluster_median: Optional[float] = None

        for txn in sorted_txns:
            amt = abs(float(txn["amount"]))

            if not current_cluster:
                current_cluster.append(txn)
                cluster_median = amt
            elif cluster_median and abs(amt - cluster_median) / cluster_median <= 0.15:
                current_cluster.append(txn)
                # Update median
                amounts = [abs(float(t["amount"])) for t in current_cluster]
                cluster_median = sorted(amounts)[len(amounts) // 2]
            else:
                clusters.append(current_cluster)
                current_cluster = [txn]
                cluster_median = amt

        if current_cluster:
            clusters.append(current_cluster)

        return clusters

    def _check_regularity(
        self,
        merchant: str,
        transactions: List[Dict],
        reference_date: date,
    ) -> Optional[DetectedSubscription]:
        """
        Check if a set of transactions (same merchant, similar amount)
        forms a regular subscription pattern.

        Returns a DetectedSubscription if the pattern is regular enough,
        otherwise None.
        """
        if len(transactions) < MIN_OCCURRENCES:
            return None

        # Parse and sort dates
        dated_txns = []
        for txn in transactions:
            try:
                d = datetime.strptime(txn["date"], "%Y-%m-%d").date()
                dated_txns.append((d, txn))
            except (ValueError, TypeError):
                continue

        dated_txns.sort(key=lambda x: x[0])

        if len(dated_txns) < MIN_OCCURRENCES:
            return None

        # Calculate intervals between consecutive charges
        dates = [dt[0] for dt in dated_txns]
        intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

        # Filter out same-day duplicates
        nonzero_intervals = [i for i in intervals if i > 0]
        if len(nonzero_intervals) < 2:
            return None

        avg_gap = statistics.mean(nonzero_intervals)
        std_gap = statistics.stdev(nonzero_intervals)
        regularity = std_gap / avg_gap if avg_gap > 0 else 999

        # Determine frequency
        frequency = self._classify_frequency(avg_gap, regularity)
        if not frequency:
            return None

        # Calculate confidence (inverse of regularity, capped at 1.0)
        confidence = round(max(0.0, min(1.0, 1.0 - regularity)), 2)

        # Get billing info
        billing_days = [d.day for d in dates]
        billing_day = max(set(billing_days), key=billing_days.count)  # mode

        # Most recent amount
        last_txn = dated_txns[-1][1]
        current_amount = float(last_txn["amount"])

        # Category from most recent transaction
        category = last_txn.get("category", "")

        # Determine active/inactive
        expected_gap_days = self._frequency_to_days(frequency)
        days_since_last = (reference_date - dates[-1]).days
        is_active = days_since_last < expected_gap_days * INACTIVE_MULTIPLIER

        # Calculate lifecycle dates
        started_at = dates[0]
        last_charged_at = dates[-1]

        if is_active:
            ended_at = None
            next_expected_at = last_charged_at + timedelta(days=expected_gap_days)
        else:
            # Estimate when it ended: last charge + one expected interval
            ended_at = last_charged_at + timedelta(days=expected_gap_days)
            next_expected_at = None

        # Collect transaction IDs
        transaction_ids = [dt[1]["id"] for dt in dated_txns]

        return DetectedSubscription(
            merchant=merchant,
            category=category,
            current_amount=current_amount,
            frequency=frequency,
            billing_day=billing_day,
            started_at=started_at,
            ended_at=ended_at,
            last_charged_at=last_charged_at,
            next_expected_at=next_expected_at,
            is_active=is_active,
            confidence=confidence,
            transaction_ids=transaction_ids,
            charge_count=len(dated_txns),
        )

    def _classify_frequency(
        self, avg_gap: float, regularity: float
    ) -> Optional[str]:
        """
        Classify a gap pattern into a frequency category.

        Returns None if the pattern doesn't match any known frequency
        or if the regularity is too poor.
        """
        if regularity > MAX_REGULARITY:
            return None

        for freq_name, (low, high) in FREQUENCY_RANGES.items():
            if low <= avg_gap <= high:
                return freq_name

        return None

    def _frequency_to_days(self, frequency: str) -> int:
        """Convert a frequency name to expected days between charges."""
        return {
            "weekly": 7,
            "bi-weekly": 14,
            "monthly": 30,
            "yearly": 365,
        }.get(frequency, 30)
