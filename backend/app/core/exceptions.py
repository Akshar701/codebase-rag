"""
Custom exception classes for clear error propagation across service layers.
Each exception maps to a specific HTTP status code in the API layer.
"""


class CodebaseRAGError(Exception):
    """Base exception for the application."""

    def __init__(self, message: str, details: str | None = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class GitHubFetchError(CodebaseRAGError):
    """Raised when fetching from GitHub fails (invalid URL, rate limit, etc.)."""
    pass


class FileFilterError(CodebaseRAGError):
    """Raised when file filtering encounters an unexpected issue."""
    pass


class ChunkingError(CodebaseRAGError):
    """Raised when the chunking pipeline fails."""
    pass


class EmbeddingError(CodebaseRAGError):
    """Raised when embedding generation fails (API error, rate limit)."""
    pass


class VectorStoreError(CodebaseRAGError):
    """Raised when Pinecone operations fail."""
    pass


class RAGQueryError(CodebaseRAGError):
    """Raised when the RAG query pipeline fails."""
    pass
