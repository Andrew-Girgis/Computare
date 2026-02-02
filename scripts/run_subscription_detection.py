#!/usr/bin/env python3
"""
Detect recurring subscriptions from transaction history.

Usage:
    python scripts/run_subscription_detection.py               # Detect and save
    python scripts/run_subscription_detection.py --dry-run      # Preview only
    python scripts/run_subscription_detection.py --show-active  # Show active subs
    python scripts/run_subscription_detection.py --show-all     # Show all subs
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from computare.subscriptions.detector import SubscriptionDetector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def format_currency(amount: float) -> str:
    return f"${abs(amount):,.2f}"


def main():
    parser = argparse.ArgumentParser(
        description="Detect recurring subscriptions from transaction history"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview detected subscriptions without saving to database",
    )
    parser.add_argument(
        "--show-active",
        action="store_true",
        help="Show currently active subscriptions from the database",
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Show all subscriptions (active + inactive) from the database",
    )
    args = parser.parse_args()

    detector = SubscriptionDetector()
    if not detector.connect():
        logger.error("Failed to connect. Check SUPABASE_URL and SUPABASE_KEY.")
        sys.exit(1)

    if args.show_active or args.show_all:
        _show_subscriptions(detector, active_only=not args.show_all)
        return

    # Run detection
    subs = detector.detect()

    if not subs:
        logger.info("No subscriptions detected.")
        return

    # Display results
    active = [s for s in subs if s.is_active]
    inactive = [s for s in subs if not s.is_active]

    print(f"\n{'=' * 90}")
    print(f"  DETECTED SUBSCRIPTIONS: {len(subs)} total ({len(active)} active, {len(inactive)} cancelled)")
    print(f"{'=' * 90}")

    if active:
        print(f"\n  ACTIVE ({len(active)})")
        print(f"  {'-' * 86}")
        print(f"  {'Merchant':<25} {'Amount':>10} {'Freq':<10} {'Since':<12} {'Last Charge':<12} {'Conf':>5} {'Charges':>7}")
        print(f"  {'-' * 86}")
        for s in sorted(active, key=lambda x: abs(x.current_amount), reverse=True):
            print(
                f"  {s.merchant:<25} "
                f"{format_currency(s.current_amount):>10} "
                f"{s.frequency:<10} "
                f"{s.started_at.strftime('%Y-%m-%d'):<12} "
                f"{s.last_charged_at.strftime('%Y-%m-%d'):<12} "
                f"{s.confidence:>5.0%} "
                f"{s.charge_count:>7}"
            )

        # Monthly total
        monthly_cost = sum(
            abs(s.current_amount) if s.frequency == "monthly"
            else abs(s.current_amount) / 12 if s.frequency == "yearly"
            else abs(s.current_amount) * 4.33 if s.frequency == "weekly"
            else abs(s.current_amount) * 2.17
            for s in active
        )
        print(f"  {'-' * 86}")
        print(f"  {'Estimated monthly total:':<48} {format_currency(monthly_cost):>10}")

    if inactive:
        print(f"\n  CANCELLED ({len(inactive)})")
        print(f"  {'-' * 86}")
        print(f"  {'Merchant':<25} {'Last Amt':>10} {'Freq':<10} {'Started':<12} {'Ended':<12} {'Conf':>5} {'Charges':>7}")
        print(f"  {'-' * 86}")
        for s in sorted(inactive, key=lambda x: x.last_charged_at, reverse=True):
            ended = s.ended_at.strftime("%Y-%m-%d") if s.ended_at else "?"
            print(
                f"  {s.merchant:<25} "
                f"{format_currency(s.current_amount):>10} "
                f"{s.frequency:<10} "
                f"{s.started_at.strftime('%Y-%m-%d'):<12} "
                f"{ended:<12} "
                f"{s.confidence:>5.0%} "
                f"{s.charge_count:>7}"
            )

    print()

    if args.dry_run:
        logger.info("Dry run — nothing saved to database.")
    else:
        detector.save(subs)
        logger.info("Subscriptions saved to database with transaction links.")


def _show_subscriptions(detector, active_only: bool):
    """Display subscriptions from the database."""
    client = detector._client
    query = client.table("subscriptions").select("*").neq("status", "dismissed")

    if active_only:
        query = query.eq("is_active", True)

    result = query.order("is_active", desc=True).order("current_amount").execute()

    if not result.data:
        print("No subscriptions found.")
        return

    active = [s for s in result.data if s["is_active"]]
    inactive = [s for s in result.data if not s["is_active"]]

    print(f"\n{'=' * 90}")
    if active_only:
        print(f"  ACTIVE SUBSCRIPTIONS ({len(active)})")
    else:
        print(f"  ALL SUBSCRIPTIONS ({len(result.data)} total: {len(active)} active, {len(inactive)} cancelled)")
    print(f"{'=' * 90}")

    for label, group in [("ACTIVE", active), ("CANCELLED", inactive)]:
        if not group:
            continue
        print(f"\n  {label} ({len(group)})")
        print(f"  {'-' * 86}")
        print(f"  {'Merchant':<25} {'Amount':>10} {'Freq':<10} {'Started':<12} {'Last/Ended':<12} {'Status':<10} {'Conf':>5}")
        print(f"  {'-' * 86}")
        for s in sorted(group, key=lambda x: abs(float(x["current_amount"])), reverse=True):
            date_col = s["last_charged_at"] if s["is_active"] else (s["ended_at"] or "?")
            print(
                f"  {s['merchant']:<25} "
                f"{format_currency(float(s['current_amount'])):>10} "
                f"{s['frequency']:<10} "
                f"{s['started_at']:<12} "
                f"{date_col:<12} "
                f"{s['status']:<10} "
                f"{float(s.get('confidence', 0)):>5.0%}"
            )

    if active:
        monthly = sum(
            abs(float(s["current_amount"])) if s["frequency"] == "monthly"
            else abs(float(s["current_amount"])) / 12 if s["frequency"] == "yearly"
            else abs(float(s["current_amount"])) * 4.33 if s["frequency"] == "weekly"
            else abs(float(s["current_amount"])) * 2.17
            for s in active
        )
        print(f"\n  Estimated monthly subscription cost: {format_currency(monthly)}")

    print()


if __name__ == "__main__":
    main()
