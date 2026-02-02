"""
Computare Categorization API.

FastAPI application for transaction categorization and merchant normalization.

Run with:
    uvicorn computare.api.app:app --reload
"""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from computare.api.routes import categorize, merchants, categories, health
from computare.api.dependencies import get_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: initialize worker and load merchant cache."""
    worker = get_worker()
    print(f"Categorization worker initialized. Cache size: {worker.cache.size}")
    yield


app = FastAPI(
    title="Computare Categorization API",
    description="Transaction categorization and merchant normalization for Computare",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(categorize.router)
app.include_router(merchants.router)
app.include_router(categories.router)
