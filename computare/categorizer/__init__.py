"""
Categorizer module for Computare.

Provides LangChain-powered transaction categorization and merchant normalization
with LangTrace observability.
"""

import os


def _init_langtrace():
    """Initialize LangTrace for observability. No-op if not configured."""
    api_key = os.environ.get("LANGTRACE_API_KEY")
    if api_key:
        try:
            from langtrace_python_sdk import langtrace
            langtrace.init(api_key=api_key)
        except ImportError:
            pass


# Auto-initialize on import
_init_langtrace()

from .worker import CategorizationWorker
from .categories import TransactionCategory, TransactionSubCategory, SUBCATEGORY_PARENT
from .cache import MerchantCache

__all__ = [
    "CategorizationWorker",
    "TransactionCategory",
    "TransactionSubCategory",
    "SUBCATEGORY_PARENT",
    "MerchantCache",
]
