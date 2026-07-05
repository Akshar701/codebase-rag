"""
Pydantic request models — validated inputs for all API endpoints.
"""

from pydantic import BaseModel, Field, field_validator
import re


class IngestRequest(BaseModel):
    """Request body for POST /api/v1/ingest."""

    github_url: str = Field(
        ...,
        description="Public GitHub repository URL",
        examples=["https://github.com/pallets/flask"],
    )

    @field_validator("github_url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        """Ensure the URL is a valid GitHub repository URL."""
        pattern = r"^https?://github\.com/[\w\-\.]+/[\w\-\.]+/?$"
        if not re.match(pattern, v.strip()):
            raise ValueError(
                "Invalid GitHub URL. Expected format: https://github.com/owner/repo"
            )
        return v.strip().rstrip("/")


class ChatRequest(BaseModel):
    """Request body for POST /api/v1/chat."""

    repository_id: str = Field(
        ...,
        description="Repository identifier (owner_repo format)",
        examples=["pallets_flask"],
    )
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Natural language question about the repository",
        examples=["How does the routing system work?"],
    )
