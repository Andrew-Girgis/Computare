"""
Pydantic request/response models for the Computare API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class TransactionInput(BaseModel):
    id: str
    description: str = ""
    merchant: str = ""
    store: str = ""
    amount: float = 0.0
    transaction_type: str = "debit"


class CategorizeRequest(BaseModel):
    transactions: List[TransactionInput]


class CategorizeFromDBRequest(BaseModel):
    """Request to categorize uncategorized transactions from the database."""
    limit: int = Field(default=500, le=5000)
    dry_run: bool = False


class CategorizationResultResponse(BaseModel):
    transaction_id: str
    raw_store: str
    normalized_merchant: str
    category: str
    source: str


class CategorizeResponse(BaseModel):
    results: List[CategorizationResultResponse]
    total: int
    from_cache: int
    from_rule: int
    from_llm: int


class BatchStatusResponse(BaseModel):
    total_processed: int
    from_cache: int
    from_rule: int
    from_llm: int
    errors: int
    cache_size: int


class MerchantMappingResponse(BaseModel):
    raw_store: str
    normalized_merchant: str
    category: str
    source: str


class MerchantUpdateRequest(BaseModel):
    raw_store: str
    normalized_merchant: str
    category: str


class CategoryResponse(BaseModel):
    name: str
    value: str


class HealthResponse(BaseModel):
    status: str
    cache_size: int
    db_connected: bool
