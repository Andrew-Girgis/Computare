"""Category listing endpoint."""

from fastapi import APIRouter
from typing import List

from computare.api.models import CategoryResponse
from computare.categorizer.categories import TransactionCategory

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryResponse])
async def list_categories():
    """List all available transaction categories."""
    return [
        CategoryResponse(name=c.name, value=c.value)
        for c in TransactionCategory
    ]
