#!/usr/bin/env python3
"""
Run batch categorization on all uncategorized transactions in Supabase.

Usage:
    python scripts/run_categorization.py               # Full run
    python scripts/run_categorization.py --dry-run      # Preview without changes
    python scripts/run_categorization.py --batch-size 100
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from computare.categorizer.worker import CategorizationWorker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Categorize transactions in Supabase using LangChain + GPT-4o-mini"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Number of transactions to fetch per page (default: 500)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview categorization without updating database",
    )
    args = parser.parse_args()

    worker = CategorizationWorker()
    if not worker.connect():
        logger.error("Failed to connect to database. Check SUPABASE_URL and SUPABASE_KEY.")
        sys.exit(1)

    logger.info(f"Connected. Merchant cache: {worker.cache.size} entries")

    if args.dry_run:
        txns = worker.fetch_uncategorized(limit=50)
        if not txns:
            logger.info("No uncategorized transactions found.")
            return

        logger.info(f"Dry run on {len(txns)} transactions:\n")
        results = worker.categorize_batch(txns, dry_run=True)

        for r in results:
            source_tag = f"[{r.source}]"
            print(
                f"  {source_tag:<10} "
                f"{r.raw_store[:45]:<45} -> "
                f"{r.normalized_merchant:<25} "
                f"[{r.category}]"
            )

        # Count by source
        from collections import Counter
        sources = Counter(r.source for r in results)
        print(f"\n  Summary: {dict(sources)}")
        llm_count = sources.get("dry_run", 0)
        if llm_count:
            print(f"  {llm_count} transactions would need LLM calls")
    else:
        stats = worker.run_full_categorization(batch_size=args.batch_size)

        logger.info("Categorization complete!")
        logger.info(f"  Total:      {stats['total']}")
        logger.info(f"  From rules: {stats['from_rule']}")
        logger.info(f"  From cache: {stats['from_cache']}")
        logger.info(f"  From LLM:   {stats['from_llm']}")
        logger.info(f"  Errors:     {stats['errors']}")
        logger.info(f"  Cache size: {worker.cache.size}")


if __name__ == "__main__":
    main()
