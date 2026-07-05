"""
File Filter — determines which files to include/exclude during repository ingestion.
Filters by extension, path pattern, and file size.
"""

from pathlib import PurePosixPath

# Extensions to include (source code, docs, config)
INCLUDED_EXTENSIONS: set[str] = {
    ".py", ".cpp", ".c", ".h", ".hpp",
    ".java", ".kt",
    ".js", ".ts", ".jsx", ".tsx",
    ".go", ".rs", ".cs",
    ".md",
    ".json", ".yaml", ".yml", ".toml",
    ".html", ".css",
    ".sql",
}

# Directory patterns to exclude
EXCLUDED_DIRECTORIES: set[str] = {
    "node_modules", ".git", "build", "dist", "coverage",
    "vendor", "venv", ".venv", "__pycache__", ".next",
    ".cache", ".idea", ".vscode", "target", "bin", "obj",
    "out", ".tox", ".mypy_cache", ".pytest_cache",
    "eggs", ".eggs", "site-packages",
}

# File name patterns to exclude
EXCLUDED_FILES: set[str] = {
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "poetry.lock", "Pipfile.lock", "composer.lock",
    "Cargo.lock", "go.sum",
}

# Binary / non-text extensions to always skip
EXCLUDED_EXTENSIONS: set[str] = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".mp4", ".mp3", ".wav", ".avi", ".mov",
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib", ".bin",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".woff", ".woff2", ".ttf", ".eot",
    ".min.js", ".min.css",
    ".pyc", ".pyo", ".class", ".o",
}


def should_include_file(
    file_path: str,
    file_size_bytes: int | None = None,
    max_file_size_kb: int = 500,
) -> bool:
    """
    Determine if a file should be included in the ingestion pipeline.

    Args:
        file_path: The file's path within the repository.
        file_size_bytes: File size in bytes (None if unknown).
        max_file_size_kb: Maximum allowed file size in kilobytes.

    Returns:
        True if the file should be processed, False otherwise.
    """
    path = PurePosixPath(file_path)

    # Check excluded directories
    for part in path.parts:
        if part in EXCLUDED_DIRECTORIES:
            return False

    # Check excluded file names
    if path.name in EXCLUDED_FILES:
        return False

    # Check file extension
    suffix = path.suffix.lower()
    if suffix in EXCLUDED_EXTENSIONS:
        return False
    if suffix not in INCLUDED_EXTENSIONS:
        return False

    # Check file size
    if file_size_bytes is not None:
        max_bytes = max_file_size_kb * 1024
        if file_size_bytes > max_bytes:
            return False

    return True


def get_language_from_extension(file_path: str) -> str:
    """Map file extension to a language identifier for chunking."""
    extension_map: dict[str, str] = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "cpp",
        ".hpp": "cpp",
        ".go": "go",
        ".rs": "rust",
        ".cs": "csharp",
        ".kt": "kotlin",
        ".html": "html",
        ".css": "css",
        ".md": "markdown",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".sql": "sql",
    }
    suffix = PurePosixPath(file_path).suffix.lower()
    return extension_map.get(suffix, "text")


def get_content_type(language: str) -> str:
    """Classify the content type based on language."""
    if language in ("markdown",):
        return "documentation"
    if language in ("json", "yaml", "toml"):
        return "config"
    return "code"
