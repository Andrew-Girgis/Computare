"""
Core categorization worker for Computare.

3-tier categorization pipeline:
  Tier 1: Description-based rules  (free, instant)
  Tier 2: Merchant cache lookup    (free, instant)
  Tier 3: LangChain → GPT-4o-mini (batched, cached after first call)
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from .categories import (
    TransactionCategory,
    KNOWN_MERCHANT_HINTS,
    DESCRIPTION_CATEGORY_RULES,
)
from .cache import MerchantCache, MerchantMapping
from .chains import build_batch_chain, get_categories_string
from .normalizer import normalize_merchant, CANONICAL_MERCHANT_NAMES

logger = logging.getLogger(__name__)

BATCH_SIZE = 30  # Transactions per LLM call


@dataclass
class CategorizationResult:
    """Result for a single transaction."""
    transaction_id: str
    raw_store: str
    normalized_merchant: str
    category: str
    source: str  # "cache", "rule", "llm", "error"
    sub_category: Optional[str] = None


class CategorizationWorker:
    """
    Main worker that categorizes transactions.

    Processing pipeline:
    1. Apply description-based rules (Payrolldep -> Income, etc.)
    2. Check known merchant keyword hints
    3. Check merchant cache for previously seen raw_store values
    4. Send remaining uncategorized to LLM in batches of 30
    5. Cache LLM results and update database
    """

    def __init__(self, supabase_client=None):
        self.cache = MerchantCache()
        self._chain = None
        self._categories_str = get_categories_string()
        self._client = supabase_client

    @property
    def chain(self):
        """Lazy-load the LangChain chain (avoids import cost if not needed)."""
        if self._chain is None:
            self._chain = build_batch_chain()
        return self._chain

    def connect(self) -> bool:
        """Initialize database connection and load cache."""
        import os

        try:
            from supabase import create_client
        except ImportError:
            logger.error("supabase-py not installed")
            return False

        if not self._client:
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")
            if url and key:
                self._client = create_client(url, key)

        self.cache.connect()
        logger.info(f"Cache loaded with {self.cache.size} entries")
        return self._client is not None

    def categorize_batch(
        self,
        transactions: List[Dict[str, Any]],
        dry_run: bool = False,
    ) -> List[CategorizationResult]:
        """
        Categorize a batch of transactions through the 3-tier pipeline.

        Each transaction dict should have:
          - id: UUID from database
          - description: str (transaction type for Scotiabank)
          - merchant: str (raw store/merchant name)
          - store: str (alias for merchant from JSON files)
        """
        results = []
        needs_llm = []

        for txn in transactions:
            txn_id = txn.get("id", "")
            description = txn.get("description", "")
            raw_store = txn.get("merchant") or txn.get("store", "")

            # Tier 1: Description-based rules
            if description in DESCRIPTION_CATEGORY_RULES:
                cat, sub_cat = DESCRIPTION_CATEGORY_RULES[description]
                results.append(CategorizationResult(
                    transaction_id=txn_id,
                    raw_store=raw_store,
                    normalized_merchant=description,
                    category=cat.value,
                    source="rule",
                    sub_category=sub_cat.value if sub_cat else None,
                ))
                continue

            if not raw_store:
                # No separate merchant field — check if description matches
                # a known merchant keyword before defaulting to Transfers
                desc_matched = self._match_known_merchant(description)
                if desc_matched:
                    merchant_name, category, sub_cat = desc_matched
                    results.append(CategorizationResult(
                        transaction_id=txn_id,
                        raw_store="",
                        normalized_merchant=merchant_name,
                        category=category.value,
                        source="rule",
                        sub_category=sub_cat,
                    ))
                elif description in DESCRIPTION_CATEGORY_RULES:
                    cat, sub_cat = DESCRIPTION_CATEGORY_RULES[description]
                    results.append(CategorizationResult(
                        transaction_id=txn_id,
                        raw_store="",
                        normalized_merchant=description,
                        category=cat.value,
                        source="rule",
                        sub_category=sub_cat.value if sub_cat else None,
                    ))
                else:
                    # Send to LLM with description as the merchant info
                    txn_copy = dict(txn)
                    txn_copy["merchant"] = description
                    needs_llm.append(txn_copy)
                continue

            # Tier 2: Known merchant keyword matching
            matched = self._match_known_merchant(raw_store)
            if matched:
                merchant_name, category, sub_cat = matched
                mapping = MerchantMapping(
                    raw_store=raw_store,
                    normalized_merchant=merchant_name,
                    category=category.value,
                    source="rule",
                    sub_category=sub_cat,
                )
                self.cache.store(mapping)
                results.append(CategorizationResult(
                    transaction_id=txn_id,
                    raw_store=raw_store,
                    normalized_merchant=merchant_name,
                    category=category.value,
                    source="rule",
                    sub_category=sub_cat,
                ))
                continue

            # Tier 2b: Cache lookup (previously categorized by LLM)
            cached = self.cache.lookup(raw_store)
            if cached:
                results.append(CategorizationResult(
                    transaction_id=txn_id,
                    raw_store=raw_store,
                    normalized_merchant=cached.normalized_merchant,
                    category=cached.category,
                    source="cache",
                    sub_category=cached.sub_category,
                ))
                continue

            # Tier 3: Needs LLM
            needs_llm.append(txn)

        # Send uncategorized to LLM in batches
        if needs_llm and not dry_run:
            llm_results = self._call_llm_batched(needs_llm)
            results.extend(llm_results)
        elif needs_llm and dry_run:
            # In dry run, mark as needing LLM
            for txn in needs_llm:
                raw_store = txn.get("merchant") or txn.get("store", "")
                results.append(CategorizationResult(
                    transaction_id=txn.get("id", ""),
                    raw_store=raw_store,
                    normalized_merchant=raw_store,
                    category="[needs LLM]",
                    source="dry_run",
                ))

        # Update database
        if not dry_run:
            self._update_database(results)

        return results

    def _match_known_merchant(
        self, raw_store: str
    ) -> Optional[Tuple[str, TransactionCategory, Optional[str]]]:
        """Check raw_store against known merchant keywords.

        First normalizes the raw_store to strip POS prefixes, location codes, etc.,
        then matches against KNOWN_MERCHANT_HINTS keywords.

        Returns (normalized_merchant_name, category, sub_category) or None.
        """
        # Normalize first for better matching
        normalized = normalize_merchant(raw_store)
        normalized_lower = normalized.lower()
        raw_lower = raw_store.lower()

        for keyword, (category, sub_cat) in KNOWN_MERCHANT_HINTS.items():
            # Check both normalized and raw (normalized is more likely to match)
            if keyword in normalized_lower or keyword in raw_lower:
                sub_value = sub_cat.value if sub_cat else None
                # Use canonical name if available, otherwise the normalized result
                display_name = CANONICAL_MERCHANT_NAMES.get(keyword, normalized)
                return display_name, category, sub_value
        return None

    def _call_llm_batched(
        self, transactions: List[Dict]
    ) -> List[CategorizationResult]:
        """Send transactions to LLM in batches of BATCH_SIZE."""
        results = []

        for i in range(0, len(transactions), BATCH_SIZE):
            batch = transactions[i: i + BATCH_SIZE]

            # Prepare input
            txn_input = [
                {
                    "raw_store": t.get("merchant") or t.get("store", ""),
                    "description": t.get("description", ""),
                }
                for t in batch
            ]

            try:
                llm_output = self.chain.invoke({
                    "count": len(batch),
                    "transactions_json": json.dumps(txn_input, indent=2),
                    "categories": self._categories_str,
                })

                # Handle different output formats
                if isinstance(llm_output, dict):
                    llm_items = llm_output.get(
                        "results",
                        llm_output.get("transactions", []),
                    )
                elif isinstance(llm_output, list):
                    llm_items = llm_output
                else:
                    llm_items = []

                # Map LLM results back to transaction IDs
                new_mappings = []
                for j, item in enumerate(llm_items):
                    if j >= len(batch):
                        break

                    txn = batch[j]
                    raw_store = txn.get("merchant") or txn.get("store", "")

                    # Validate category
                    category = item.get("category", "Retail & Shopping")
                    if not self._is_valid_category(category):
                        category = "Retail & Shopping"

                    # Normalize the merchant name from LLM (or use our normalizer as fallback)
                    llm_merchant = item.get("merchant", "")
                    merchant = normalize_merchant(raw_store) if not llm_merchant else llm_merchant

                    mapping = MerchantMapping(
                        raw_store=raw_store,
                        normalized_merchant=merchant,
                        category=category,
                        source="llm",
                    )
                    new_mappings.append(mapping)

                    results.append(CategorizationResult(
                        transaction_id=txn.get("id", ""),
                        raw_store=raw_store,
                        normalized_merchant=merchant,
                        category=category,
                        source="llm",
                    ))

                # Cache all new mappings
                try:
                    self.cache.store_batch(new_mappings)
                except Exception as cache_err:
                    logger.warning(f"Cache batch store failed, storing individually: {cache_err}")
                    for m in new_mappings:
                        try:
                            self.cache.store(m)
                        except Exception:
                            pass

                batch_num = i // BATCH_SIZE + 1
                total_batches = (len(transactions) + BATCH_SIZE - 1) // BATCH_SIZE
                logger.info(
                    f"LLM batch {batch_num}/{total_batches}: "
                    f"categorized {len(batch)} transactions"
                )

                # Small delay between batches to avoid rate limits
                if i + BATCH_SIZE < len(transactions):
                    time.sleep(0.5)

            except Exception as e:
                logger.error(f"LLM batch error: {e}")
                for txn in batch:
                    raw_store = txn.get("merchant") or txn.get("store", "")
                    results.append(CategorizationResult(
                        transaction_id=txn.get("id", ""),
                        raw_store=raw_store,
                        normalized_merchant=raw_store,
                        category="Retail & Shopping",
                        source="error",
                    ))

        return results

    def _is_valid_category(self, category: str) -> bool:
        """Check if category is in the allowed set."""
        valid = {c.value for c in TransactionCategory}
        return category in valid

    def _update_database(self, results: List[CategorizationResult]):
        """Update transactions in Supabase with merchant + category + sub_category."""
        if not self._client:
            return

        for result in results:
            if not result.transaction_id:
                continue
            try:
                update_data: Dict[str, Any] = {
                    "merchant": result.normalized_merchant,
                    "category": result.category,
                }
                if result.sub_category:
                    update_data["sub_category"] = result.sub_category
                self._client.table("transactions").update(
                    update_data
                ).eq("id", result.transaction_id).execute()
            except Exception as e:
                logger.error(
                    f"DB update failed for {result.transaction_id}: {e}"
                )

    def fetch_uncategorized(self, limit: int = 500) -> List[Dict]:
        """Fetch transactions from Supabase that have no category."""
        if not self._client:
            return []

        result = (
            self._client.table("transactions")
            .select("id, description, merchant, amount, transaction_type, account_id")
            .is_("category", "null")
            .limit(limit)
            .execute()
        )

        return result.data or []

    def run_full_categorization(self, batch_size: int = 500) -> Dict[str, int]:
        """
        Run categorization on all uncategorized transactions.

        Fetches in pages and processes each page.
        Returns summary stats.
        """
        stats = {
            "total": 0,
            "from_cache": 0,
            "from_rule": 0,
            "from_llm": 0,
            "errors": 0,
        }

        while True:
            transactions = self.fetch_uncategorized(limit=batch_size)
            if not transactions:
                break

            results = self.categorize_batch(transactions)
            stats["total"] += len(results)

            for r in results:
                if r.source == "cache":
                    stats["from_cache"] += 1
                elif r.source == "rule":
                    stats["from_rule"] += 1
                elif r.source == "llm":
                    stats["from_llm"] += 1
                elif r.source == "error":
                    stats["errors"] += 1

            logger.info(f"Processed {stats['total']} transactions so far...")

            if len(transactions) < batch_size:
                break

        return stats
