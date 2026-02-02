"""
FastAPI dependency injection for Computare.
"""

from functools import lru_cache

from computare.categorizer.worker import CategorizationWorker


@lru_cache()
def get_worker() -> CategorizationWorker:
    """Singleton worker instance, shared across all requests."""
    worker = CategorizationWorker()
    worker.connect()
    return worker
