"""
Subscription detection module for Computare.

Identifies recurring charges from transaction history and tracks
subscription lifecycle (active, cancelled, price changes).
"""

from .detector import SubscriptionDetector

__all__ = ["SubscriptionDetector"]
