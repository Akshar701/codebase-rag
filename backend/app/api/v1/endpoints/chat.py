"""
POST /api/v1/chat — RAG Query and Chat Endpoint.

Accepts user questions about an ingested repository, performs semantic search,
and generates grounded answers using the Gemini LLM.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.models.requests import ChatRequest
from app.models.responses import ChatResponse, ErrorResponse
from app.core.logging import logger
from app.core.exceptions import CodebaseRAGError
from app.api.v1.deps import get_rag_service
from app.services.rag_service import RAGService

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid repository namespace"},
        404: {"model": ErrorResponse, "description": "Repository context not found"},
        500: {"model": ErrorResponse, "description": "AI generation or pipeline error"},
    },
    summary="Ask a question about an ingested repository",
    description="Performs semantic search over chunks of a repository and generates an LLM answer.",
)
async def chat_with_repository(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> ChatResponse:
    """Answers a question about an ingested repository using semantic code retrieval."""
    logger.info(f"💬 Chat request received for namespace: '{request.repository_id}'")

    try:
        response = await rag_service.answer_question(
            repository_id=request.repository_id,
            question=request.question,
        )
        return response

    except CodebaseRAGError as e:
        # Re-raise custom application exceptions to be handled by global handlers in main.py
        raise
    except Exception as e:
        logger.error(f"Chat pipeline failed unexpectedly: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during chat processing: {str(e)}"
        )
