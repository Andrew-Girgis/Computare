"""
Two-tier merchant cache for Computare.

Tier 1: In-memory dict for fast lookups during batch processing.
Tier 2: Supabase merchant_cache table for persistence across runs.
"""

import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None


@dataclass
class MerchantMapping:
    """A cached mapping from raw store text to normalized merchant + category."""
    raw_store: str
    normalized_merchant: str
    category: str
    confidence: float = 1.0
    source: str = "llm"  # "llm", "manual", "rule"
    sub_category: Optional[str] = None


class MerchantCache:
    """
    Two-tier merchant cache:
    1. In-memory dict for fast lookups during batch processing
    2. Supabase merchant_cache table for persistence across runs
    """

    def __init__(self):
        self._memory_cache: Dict[str, MerchantMapping] = {}
        self._client: Optional[Client] = None

    def connect(self) -> bool:
        """Connect to Supabase and load existing cache into memory."""
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key or not create_client:
            return False

        try:
            self._client = create_client(url, key)
            self._load_from_db()
            return True
        except Exception:
            return False

    def _load_from_db(self):
        """Load all cached mappings into memory."""
        if not self._client:
            return

        result = self._client.table("merchant_cache").select("*").execute()
        for row in result.data or []:
            mapping = MerchantMapping(
                raw_store=row["raw_store"],
                normalized_merchant=row["normalized_merchant"],
                category=row["category"],
                confidence=row.get("confidence", 1.0),
                source=row.get("source", "llm"),
                sub_category=row.get("sub_category"),
            )
            self._memory_cache[row["raw_store"]] = mapping

    def lookup(self, raw_store: str) -> Optional[MerchantMapping]:
        """Look up a raw store value. Returns None if not cached."""
        return self._memory_cache.get(raw_store)

    def lookup_batch(
        self, raw_stores: List[str]
    ) -> Tuple[Dict[str, MerchantMapping], List[str]]:
        """
        Look up a batch of raw store values.

        Returns:
            hits: dict of raw_store -> MerchantMapping for cached entries
            misses: list of raw_store values not in cache
        """
        hits = {}
        misses = []
        for raw in raw_stores:
            mapping = self._memory_cache.get(raw)
            if mapping:
                hits[raw] = mapping
            else:
                misses.append(raw)
        return hits, misses

    def store(self, mapping: MerchantMapping):
        """Store a mapping in both memory and database."""
        self._memory_cache[mapping.raw_store] = mapping
        if self._client:
            row = {
                "raw_store": mapping.raw_store,
                "normalized_merchant": mapping.normalized_merchant,
                "category": mapping.category,
                "confidence": mapping.confidence,
                "source": mapping.source,
            }
            if mapping.sub_category:
                row["sub_category"] = mapping.sub_category
            self._client.table("merchant_cache").upsert(
                row, on_conflict="raw_store",
            ).execute()

    def store_batch(self, mappings: List[MerchantMapping]):
        """Store multiple mappings at once. Deduplicates by raw_store."""
        for m in mappings:
            self._memory_cache[m.raw_store] = m

        if self._client and mappings:
            # Deduplicate: keep last occurrence per raw_store
            seen: Dict[str, MerchantMapping] = {}
            for m in mappings:
                seen[m.raw_store] = m
            rows = []
            for m in seen.values():
                row = {
                    "raw_store": m.raw_store,
                    "normalized_merchant": m.normalized_merchant,
                    "category": m.category,
                    "confidence": m.confidence,
                    "source": m.source,
                }
                if m.sub_category:
                    row["sub_category"] = m.sub_category
                rows.append(row)
            self._client.table("merchant_cache").upsert(
                rows, on_conflict="raw_store"
            ).execute()

    def get_all(self) -> List[MerchantMapping]:
        """Return all cached mappings."""
        return list(self._memory_cache.values())

    @property
    def size(self) -> int:
        return len(self._memory_cache)
