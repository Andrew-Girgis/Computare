"""Merchant cache management endpoints."""

from fastapi import APIRouter, Depends, Query
from typing import List

from computare.api.models import MerchantMappingResponse, MerchantUpdateRequest
from computare.api.dependencies import get_worker
from computare.categorizer.worker import CategorizationWorker
from computare.categorizer.cache import MerchantMapping

router = APIRouter(prefix="/merchants", tags=["merchants"])


@router.get("/", response_model=List[MerchantMappingResponse])
async def list_merchants(
    worker: CategorizationWorker = Depends(get_worker),
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    category: str = Query(default=None),
):
    """List cached merchant mappings with optional category filter."""
    all_mappings = worker.cache.get_all()

    if category:
        all_mappings = [m for m in all_mappings if m.category == category]

    page = all_mappings[offset: offset + limit]
    return [
        MerchantMappingResponse(
            raw_store=m.raw_store,
            normalized_merchant=m.normalized_merchant,
            category=m.category,
            source=m.source,
        )
        for m in page
    ]


@router.put("/", response_model=MerchantMappingResponse)
async def update_merchant(
    request: MerchantUpdateRequest,
    worker: CategorizationWorker = Depends(get_worker),
):
    """Manually override a merchant mapping (for corrections)."""
    mapping = MerchantMapping(
        raw_store=request.raw_store,
        normalized_merchant=request.normalized_merchant,
        category=request.category,
        source="manual",
    )
    worker.cache.store(mapping)

    # Also update all transactions with this raw merchant in the database
    if worker._client:
        worker._client.table("transactions").update({
            "merchant": request.normalized_merchant,
            "category": request.category,
        }).eq("merchant", request.raw_store).execute()

    return MerchantMappingResponse(
        raw_store=mapping.raw_store,
        normalized_merchant=mapping.normalized_merchant,
        category=mapping.category,
        source=mapping.source,
    )
