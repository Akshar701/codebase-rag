"""
Chunking Service — intelligently splits source code and documentation files into semantic chunks.

Features:
- Language-aware splitting using LangChain's RecursiveCharacterTextSplitter
- Line number tracking (calculates start_line and end_line for every chunk)
- Parent context extraction (e.g. enclosing class/function name)
- Import extraction (tracks top-level imports in the file)
- Rich metadata schema per chunk
"""

from typing import Any
from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

from app.core.config import settings
from app.core.logging import logger
from app.utils.file_filter import get_language_from_extension, get_content_type
from app.utils.text_processing import clean_text, extract_imports, extract_parent_context
from app.services.github_service import RepoFile, RepoMetadata


@dataclass
class CodeChunk:
    """Represents a single processed chunk ready for embedding and vector storage."""
    content: str
    metadata: dict[str, Any]


class ChunkingService:
    """Intelligently splits repository files into context-rich chunks."""

    # Map our language identifiers to LangChain's Language enum
    LANGCHAIN_LANGUAGE_MAP = {
        "python": Language.PYTHON,
        "javascript": Language.JS,
        "typescript": Language.TS,
        "java": Language.JAVA,
        "cpp": Language.CPP,
        "go": Language.GO,
        "rust": Language.RUST,
        "markdown": Language.MARKDOWN,
        "html": Language.HTML,
    }

    def __init__(
        self,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._generic_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        self._splitters: dict[Language, RecursiveCharacterTextSplitter] = {}

    def _get_splitter(self, language: str) -> RecursiveCharacterTextSplitter:
        """Get or create a language-aware splitter."""
        lc_lang = self.LANGCHAIN_LANGUAGE_MAP.get(language)
        if not lc_lang:
            return self._generic_splitter

        if lc_lang not in self._splitters:
            self._splitters[lc_lang] = RecursiveCharacterTextSplitter.from_language(
                language=lc_lang,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        return self._splitters[lc_lang]

    def _find_line_numbers(self, full_text: str, chunk_text: str, last_index: int = 0) -> tuple[int, int, int]:
        """
        Locates the line numbers for a chunk within the full text.
        Returns (start_line, end_line, next_search_index).
        Line numbers are 1-indexed.
        """
        # Find the starting character index of the chunk content, starting from last_index
        char_idx = full_text.find(chunk_text, last_index)
        if char_idx == -1:
            # Fallback: search from beginning if we lost alignment
            char_idx = full_text.find(chunk_text)
            if char_idx == -1:
                return 1, 1, last_index

        # Count newlines to determine line number
        start_line = full_text.count("\n", 0, char_idx) + 1
        chunk_newlines = chunk_text.count("\n")
        end_line = start_line + chunk_newlines

        next_search_index = char_idx + len(chunk_text)
        return start_line, end_line, next_search_index

    def chunk_file(
        self,
        file: RepoFile,
        repo_metadata: RepoMetadata,
    ) -> list[CodeChunk]:
        """
        Splits a single file into chunks and attaches rich metadata.

        Args:
            file: The file object containing path and content
            repo_metadata: Parent repository metadata (repo, owner, branch)

        Returns:
            List of CodeChunk objects
        """
        cleaned_content = clean_text(file.content)
        if not cleaned_content.strip():
            return []

        language = get_language_from_extension(file.path)
        content_type = get_content_type(language)
        splitter = self._get_splitter(language)

        try:
            raw_chunks = splitter.split_text(cleaned_content)
        except Exception as e:
            logger.warning(f"Language-aware split failed for {file.path} ({language}): {e}. Falling back to generic split.")
            raw_chunks = self._generic_splitter.split_text(cleaned_content)

        # Extract file-level imports once
        file_imports = extract_imports(cleaned_content, language)

        code_chunks: list[CodeChunk] = []
        last_index = 0
        total_chunks = len(raw_chunks)

        for idx, chunk_text in enumerate(raw_chunks):
            # Calculate line numbers
            start_line, end_line, last_index = self._find_line_numbers(
                cleaned_content, chunk_text, last_index
            )

            # Try to resolve context (e.g. enclosing class name or function signature)
            parent_context = extract_parent_context(chunk_text, language)

            # Build metadata matching our schema
            metadata = {
                "repository": f"{repo_metadata.owner}/{repo_metadata.repo}",
                "branch": repo_metadata.branch,
                "file_path": file.path,
                "file_name": file.path.split("/")[-1],
                "language": language,
                "chunk_index": idx,
                "total_chunks": total_chunks,
                "start_line": start_line,
                "end_line": end_line,
                "content_type": content_type,
                "parent_context": parent_context or "",
                "imports": ", ".join(file_imports)[:500],  # Join to string under size limits
            }

            code_chunks.append(CodeChunk(content=chunk_text, metadata=metadata))

        return code_chunks

    def chunk_repository(
        self,
        files: list[RepoFile],
        repo_metadata: RepoMetadata,
    ) -> list[CodeChunk]:
        """
        Process a list of files, chunking them, and returning a flat list of CodeChunks.
        """
        all_chunks: list[CodeChunk] = []
        logger.info(f"Starting chunking for {len(files)} files in repository")

        for file in files:
            chunks = self.chunk_file(file, repo_metadata)
            all_chunks.extend(chunks)

        logger.info(f"Generated {len(all_chunks)} chunks from {len(files)} files")
        return all_chunks
