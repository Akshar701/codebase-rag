"""
POST /api/v1/ingest — Repository Ingestion Pipeline.

Downloads, filters, chunks, embeds, and stores a public GitHub repository.
Isolates each repository under a Pinecone namespace based on its owner and name.
"""

import time
from fastapi import APIRouter, Depends, HTTPException

from app.models.requests import IngestRequest
from app.models.responses import IngestResponse, IngestionStatistics, ErrorResponse
from app.core.logging import logger
from app.core.exceptions import CodebaseRAGError
from app.api.v1.deps import (
    get_github_service,
    get_chunking_service,
    get_embedding_service,
    get_vector_store_service,
)
from app.services.github_service import GitHubService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService

router = APIRouter()


@router.post(
    "/ingest",
    response_model=IngestResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid repository or access error"},
        500: {"model": ErrorResponse, "description": "Pipeline execution error"},
    },
    summary="Ingest a GitHub repository",
    description="Full RAG Ingestion: downloads, filters, chunks, embeds, and upserts a public repo.",
)
async def ingest_repository(
    request: IngestRequest,
    github_service: GitHubService = Depends(get_github_service),
    chunking_service: ChunkingService = Depends(get_chunking_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_store: VectorStoreService = Depends(get_vector_store_service),
) -> IngestResponse:
    """Runs the ingestion pipeline and returns statistics."""
    logger.info(f"🚀 Starting ingestion pipeline for URL: {request.github_url}")
    pipeline_start = time.time()

    try:
        # Step 1: Fetch and download filtered repository files
        fetch_result = await github_service.fetch_repository(request.github_url)
        meta = fetch_result.metadata
        
        # Unique namespace identifier e.g. pallets_flask
        repository_id = f"{meta.owner}_{meta.repo}"

        # Step 2: Generate intelligent chunks
        chunks = chunking_service.chunk_repository(fetch_result.files, meta)
        
        # Step 3: Embed chunk texts
        chunk_texts = [chunk.content for chunk in chunks]
        
        embedding_start = time.time()
        embeddings = await embedding_service.embed_texts(chunk_texts)
        embedding_duration = time.time() - embedding_start

        # Step 4: Clear namespace (for safe re-ingestion) and upsert to Pinecone
        await vector_store.clear_namespace(repository_id)
        await vector_store.upsert_chunks(chunks, embeddings, repository_id)

        # Step 5: Calculate pipeline statistics
        total_duration = time.time() - pipeline_start
        
        stats = IngestionStatistics(
            files_processed=meta.files_after_filter,
            files_skipped=len(fetch_result.skipped_files),
            chunks_generated=len(chunks),
            embedding_time_seconds=round(embedding_duration, 2),
            total_duration_seconds=round(total_duration, 2),
        )

        logger.info(
            f"✅ Ingestion successful for {meta.owner}/{meta.repo}. "
            f"Processed {meta.files_after_filter} files, generated {len(chunks)} chunks in {total_duration:.2f}s."
        )

        return IngestResponse(
            status="success",
            repository_id=repository_id,
            statistics=stats,
        )

    except CodebaseRAGError as e:
        # Re-raise standard custom exceptions to be handled by main.py's global handlers
        raise
    except Exception as e:
        logger.error(f"Ingestion pipeline failed unexpectedly: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during ingestion: {str(e)}"
        )
