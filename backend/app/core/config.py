"""
Pydantic Settings — loads configuration from environment variables.
All secrets and tunable parameters are centralized here.
"""

from typing import Any, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application configuration loaded from .env file or environment."""

    # --- Google Gemini (free tier) ---
    google_api_key: str = Field(..., description="Google AI Studio API key")
    gemini_chat_model: str = Field(
        default="gemini-3.5-flash",
        description="Gemini model for chat completions",
    )
    gemini_embedding_model: str = Field(
        default="models/gemini-embedding-002",
        description="Gemini model for text embeddings",
    )
    embedding_dimensions: int = Field(
        default=3072,
        description="Dimensionality of Gemini embeddings",
    )

    # --- Pinecone (free tier) ---
    pinecone_api_key: str = Field(..., description="Pinecone API key")
    pinecone_index: str = Field(
        default="codebase-rag",
        description="Pinecone index name",
    )

    # --- GitHub ---
    github_token: str = Field(
        default="",
        description="Optional GitHub token for higher rate limits",
    )

    # --- Server ---
    fastapi_port: int = Field(default=8000, description="FastAPI server port")
    cors_origins: Union[list[str], str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:3003",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3002",
            "http://127.0.0.1:3003",
        ],
        description="Allowed CORS origins. Set CORS_ORIGINS env var with comma-separated URLs for production.",
    )

    # --- Chunking ---
    chunk_size: int = Field(default=1500, description="Target chunk size in characters")
    chunk_overlap: int = Field(default=200, description="Chunk overlap in characters")
    max_file_size_kb: int = Field(
        default=500,
        description="Maximum file size to process (KB)",
    )

    # --- RAG ---
    top_k: int = Field(default=8, description="Number of chunks to retrieve")
    embedding_batch_size: int = Field(
        default=50,
        description="Texts per embedding API call",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton instance — imported throughout the app
settings = Settings()
