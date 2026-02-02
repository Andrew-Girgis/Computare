"""Transaction categorization endpoints."""

from fastapi import APIRouter, Depends

from computare.api.models import (
    CategorizeRequest,
    CategorizeResponse,
    CategorizeFromDBRequest,
    BatchStatusResponse,
    CategorizationResultResponse,
)
from computare.api.dependencies import get_worker
from computare.categorizer.worker import CategorizationWorker

router = APIRouter(prefix="/categorize", tags=["categorize"])


@router.post("/", response_model=CategorizeResponse)
async def categorize_transactions(
    request: CategorizeRequest,
    worker: CategorizationWorker = Depends(get_worker),
):
    """Categorize a list of transactions provided in the request body."""
    txns = [t.model_dump() for t in request.transactions]
    results = worker.categorize_batch(txns)

    stats = {"from_cache": 0, "from_rule": 0, "from_llm": 0}
    for r in results:
        if r.source in stats:
            stats[r.source] += 1

    return CategorizeResponse(
        results=[
            CategorizationResultResponse(
                transaction_id=r.transaction_id,
                raw_store=r.raw_store,
                normalized_merchant=r.normalized_merchant,
                category=r.category,
                source=r.source,
            )
            for r in results
        ],
        total=len(results),
        **stats,
    )


@router.post("/batch", response_model=BatchStatusResponse)
async def run_batch_categorization(
    request: CategorizeFromDBRequest,
    worker: CategorizationWorker = Depends(get_worker),
):
    """Run categorization on uncategorized transactions from the database."""
    if request.dry_run:
        txns = worker.fetch_uncategorized(limit=request.limit)
        results = worker.categorize_batch(txns, dry_run=True)
        stats = {"from_cache": 0, "from_rule": 0, "from_llm": 0, "errors": 0}
        for r in results:
            if r.source == "cache":
                stats["from_cache"] += 1
            elif r.source == "rule":
                stats["from_rule"] += 1
            elif r.source == "dry_run":
                stats["from_llm"] += 1  # Would be LLM
        return BatchStatusResponse(
            total_processed=len(results),
            cache_size=worker.cache.size,
            **stats,
        )

    stats = worker.run_full_categorization(batch_size=request.limit)
    return BatchStatusResponse(
        total_processed=stats["total"],
        from_cache=stats["from_cache"],
        from_rule=stats["from_rule"],
        from_llm=stats["from_llm"],
        errors=stats["errors"],
        cache_size=worker.cache.size,
    )
