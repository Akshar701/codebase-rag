"""
Dependency Injection Providers — centralizes service instances for FastAPI routing endpoints.
Allows easy mocking during testing.
"""

from functools import lru_cache
from app.services.github_service import GitHubService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.services.rag_service import RAGService


@lru_cache
def get_github_service() -> GitHubService:
    """Return a singleton instance of GitHubService."""
    return GitHubService()


@lru_cache
def get_chunking_service() -> ChunkingService:
    """Return a singleton instance of ChunkingService."""
    return ChunkingService()


@lru_cache
def get_embedding_service() -> EmbeddingService:
    """Return a singleton instance of EmbeddingService."""
    return EmbeddingService()


@lru_cache
def get_vector_store_service() -> VectorStoreService:
    """Return a singleton instance of VectorStoreService."""
    return VectorStoreService()


@lru_cache
def get_rag_service() -> RAGService:
    """Return a singleton instance of RAGService."""
    return RAGService(
        embedding_service=get_embedding_service(),
        vector_store=get_vector_store_service(),
    )
