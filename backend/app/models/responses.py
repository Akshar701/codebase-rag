"""
Pydantic response models — structured outputs for all API endpoints.
"""

from pydantic import BaseModel, Field


class IngestionStatistics(BaseModel):
    """Statistics returned after repository ingestion."""

    files_processed: int = Field(description="Number of files successfully processed")
    files_skipped: int = Field(description="Number of files skipped by filters")
    chunks_generated: int = Field(description="Total chunks created")
    embedding_time_seconds: float = Field(description="Time spent on embedding generation")
    total_duration_seconds: float = Field(description="Total pipeline duration")


class IngestResponse(BaseModel):
    """Response body for POST /api/v1/ingest."""

    status: str = Field(default="success")
    repository_id: str = Field(description="Repository identifier for subsequent queries")
    statistics: IngestionStatistics


class SourceChunk(BaseModel):
    """A single retrieved source chunk with metadata."""

    file_path: str = Field(description="Path of the source file")
    start_line: int | None = Field(default=None, description="Start line number")
    end_line: int | None = Field(default=None, description="End line number")
    snippet: str = Field(description="Code/text snippet")
    relevance_score: float = Field(description="Cosine similarity score")


class ChatResponse(BaseModel):
    """Response body for POST /api/v1/chat."""

    answer: str = Field(description="LLM-generated answer")
    sources: list[SourceChunk] = Field(
        default_factory=list,
        description="Retrieved source chunks used to generate the answer",
    )


class ErrorResponse(BaseModel):
    """Standard error response body."""

    error: str = Field(description="Error type")
    message: str = Field(description="Human-readable error message")
    details: str | None = Field(default=None, description="Additional details")
