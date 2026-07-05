"""
v1 API Router — aggregates all v1 endpoint routers under /api/v1.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import ingest, chat

v1_router = APIRouter(prefix="/api/v1", tags=["v1"])

v1_router.include_router(ingest.router, tags=["ingestion"])
v1_router.include_router(chat.router, tags=["chat"])
