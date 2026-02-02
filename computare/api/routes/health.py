"""Health check endpoint."""

from fastapi import APIRouter, Depends

from computare.api.models import HealthResponse
from computare.api.dependencies import get_worker
from computare.categorizer.worker import CategorizationWorker

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    worker: CategorizationWorker = Depends(get_worker),
):
    return HealthResponse(
        status="ok",
        cache_size=worker.cache.size,
        db_connected=worker._client is not None,
    )
