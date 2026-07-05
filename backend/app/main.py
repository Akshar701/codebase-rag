"""
FastAPI Application Entry Point.

Sets up the app with:
- CORS middleware (allowing frontend at localhost:3000)
- v1 API router
- Global exception handlers
- Health check endpoint
- Lifespan management for startup/shutdown
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import v1_router
from app.api.v1.deps import get_github_service
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    CodebaseRAGError,
    GitHubFetchError,
    ChunkingError,
    EmbeddingError,
    VectorStoreError,
    RAGQueryError,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan — runs on startup and shutdown."""
    logger.info("🚀 Starting Codebase RAG API server")
    logger.info(f"   Gemini Chat Model: {settings.gemini_chat_model}")
    logger.info(f"   Gemini Embedding Model: {settings.gemini_embedding_model}")
    logger.info(f"   Pinecone Index: {settings.pinecone_index}")
    logger.info(f"   Chunk Size: {settings.chunk_size} | Overlap: {settings.chunk_overlap}")
    yield
    # Cleanup: close the httpx client used by GitHubService
    try:
        github_service = get_github_service()
        await github_service.close()
        logger.info("Closed GitHub HTTP client")
    except Exception:
        pass
    logger.info("👋 Shutting down Codebase RAG API server")


def create_app() -> FastAPI:
    """Factory function to create and configure the FastAPI application."""

    app = FastAPI(
        title="AI Codebase Assistant",
        description="RAG-powered Q&A over GitHub repositories using Gemini + Pinecone",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # --- CORS Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Routers ---
    app.include_router(v1_router)

    # --- Health Check ---
    @app.get("/health", tags=["system"])
    async def health_check():
        return {"status": "healthy", "version": "1.0.0"}

    # --- Exception Handlers ---
    @app.exception_handler(GitHubFetchError)
    async def github_error_handler(request: Request, exc: GitHubFetchError):
        logger.error(f"GitHub error: {exc.message}")
        return JSONResponse(
            status_code=400,
            content={"error": "github_error", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(ChunkingError)
    async def chunking_error_handler(request: Request, exc: ChunkingError):
        logger.error(f"Chunking error: {exc.message}")
        return JSONResponse(
            status_code=500,
            content={"error": "chunking_error", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(EmbeddingError)
    async def embedding_error_handler(request: Request, exc: EmbeddingError):
        logger.error(f"Embedding error: {exc.message}")
        return JSONResponse(
            status_code=500,
            content={"error": "embedding_error", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(VectorStoreError)
    async def vector_store_error_handler(request: Request, exc: VectorStoreError):
        logger.error(f"Vector store error: {exc.message}")
        return JSONResponse(
            status_code=500,
            content={"error": "vector_store_error", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(RAGQueryError)
    async def rag_error_handler(request: Request, exc: RAGQueryError):
        logger.error(f"RAG query error: {exc.message}")
        return JSONResponse(
            status_code=500,
            content={"error": "rag_error", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(CodebaseRAGError)
    async def generic_app_error_handler(request: Request, exc: CodebaseRAGError):
        logger.error(f"Application error: {exc.message}")
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "message": exc.message, "details": exc.details},
        )

    return app


# Create the app instance — used by uvicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.fastapi_port,
        reload=True,
        log_level="info",
    )
