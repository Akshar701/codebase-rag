"""
GitHub Service — fetches repository metadata and file contents from the GitHub REST API.

Implements:
- URL parsing and validation
- Repository tree fetching (recursive)
- File content downloading (parallel, rate-limit aware)
- Automatic branch detection (main/master)
- Exponential backoff for rate limits
"""

import asyncio
import base64
import re
from dataclasses import dataclass, field

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import GitHubFetchError
from app.utils.file_filter import should_include_file


@dataclass
class RepoFile:
    """Represents a single file downloaded from a GitHub repository."""
    path: str
    content: str
    size: int
    sha: str


@dataclass
class RepoMetadata:
    """Metadata about the fetched repository."""
    owner: str
    repo: str
    branch: str
    total_files_found: int
    files_after_filter: int


@dataclass
class FetchResult:
    """Complete result from fetching a repository."""
    metadata: RepoMetadata
    files: list[RepoFile] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)


class GitHubService:
    """Handles all interactions with the GitHub REST API."""

    BASE_URL = "https://api.github.com"
    # Max concurrent downloads to avoid hammering the API
    MAX_CONCURRENT_DOWNLOADS = 10
    # Max file size for individual file download (raw content endpoint)
    RAW_CONTENT_MAX_SIZE = settings.max_file_size_kb * 1024

    def __init__(self):
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CodebaseRAG/1.0",
        }
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"
            logger.info("GitHub Service initialized with authentication token")
        else:
            logger.info("GitHub Service initialized without token (60 req/hr limit)")

        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=30.0,
            follow_redirects=True,
        )

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    @staticmethod
    def parse_github_url(url: str) -> tuple[str, str]:
        """
        Extract owner and repo name from a GitHub URL.

        Args:
            url: GitHub URL like https://github.com/owner/repo

        Returns:
            Tuple of (owner, repo)

        Raises:
            GitHubFetchError: If URL format is invalid
        """
        pattern = r"^https?://github\.com/([\w\-\.]+)/([\w\-\.]+?)(?:\.git)?/?$"
        match = re.match(pattern, url.strip())
        if not match:
            raise GitHubFetchError(
                message="Invalid GitHub URL format",
                details=f"Expected: https://github.com/owner/repo, got: {url}",
            )
        return match.group(1), match.group(2)

    async def _detect_default_branch(self, owner: str, repo: str) -> str:
        """
        Detect the default branch of a repository.
        Returns 'main', 'master', or whatever the repo uses.
        """
        try:
            response = await self._client.get(f"/repos/{owner}/{repo}")
            response.raise_for_status()
            data = response.json()
            branch = data.get("default_branch", "main")
            logger.info(f"Detected default branch: {branch}")
            return branch
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise GitHubFetchError(
                    message=f"Repository not found: {owner}/{repo}",
                    details="Make sure the repository exists and is public.",
                )
            if e.response.status_code == 403:
                raise GitHubFetchError(
                    message="GitHub API rate limit exceeded",
                    details="Add a GITHUB_TOKEN to your .env file for higher limits.",
                )
            raise GitHubFetchError(
                message=f"Failed to fetch repository info: {e.response.status_code}",
                details=str(e),
            )

    async def _fetch_tree(self, owner: str, repo: str, branch: str) -> list[dict]:
        """
        Fetch the full recursive tree of the repository.
        Returns list of tree entries (blobs only, not trees).
        """
        url = f"/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        logger.info(f"Fetching repository tree: {owner}/{repo}@{branch}")

        try:
            response = await self._client.get(url)
            response.raise_for_status()
            data = response.json()

            if data.get("truncated"):
                logger.warning(
                    "Repository tree was truncated — very large repo. "
                    "Some files may be missing."
                )

            # Filter to blobs (files) only, not subtrees
            blobs = [
                entry for entry in data.get("tree", [])
                if entry.get("type") == "blob"
            ]
            logger.info(f"Found {len(blobs)} files in repository tree")
            return blobs

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise GitHubFetchError(
                    message=f"Branch '{branch}' not found in {owner}/{repo}",
                    details="The repository may be empty or the branch may not exist.",
                )
            raise GitHubFetchError(
                message=f"Failed to fetch repository tree: {e.response.status_code}",
                details=str(e),
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        reraise=True,
    )
    async def _download_file(
        self, owner: str, repo: str, path: str, branch: str
    ) -> str | None:
        """
        Download a single file's content from the repository.
        Uses the Contents API which returns base64-encoded content for files < 1MB,
        and falls back to raw content for larger files.

        Returns:
            File content as string, or None if download fails.
        """
        try:
            # Use the Contents API — returns base64 for files up to 1MB
            url = f"/repos/{owner}/{repo}/contents/{path}?ref={branch}"
            response = await self._client.get(url)
            response.raise_for_status()
            data = response.json()

            if data.get("encoding") == "base64" and data.get("content"):
                content_bytes = base64.b64decode(data["content"])
                try:
                    return content_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    logger.debug(f"Skipping binary file: {path}")
                    return None

            # If content is not base64, try download_url
            download_url = data.get("download_url")
            if download_url:
                raw_response = await self._client.get(
                    download_url,
                    follow_redirects=True,
                )
                raw_response.raise_for_status()
                return raw_response.text

            return None

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                remaining = e.response.headers.get("X-RateLimit-Remaining", "?")
                logger.warning(f"Rate limited downloading {path}. Remaining: {remaining}")
                raise  # Let tenacity retry
            if e.response.status_code == 404:
                logger.debug(f"File not found (may have been deleted): {path}")
                return None
            logger.warning(f"Failed to download {path}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error downloading {path}: {e}")
            return None

    async def fetch_repository(self, github_url: str) -> FetchResult:
        """
        Full repository fetch pipeline:
        1. Parse URL → owner/repo
        2. Detect default branch
        3. Fetch recursive tree
        4. Filter files by extension/path/size
        5. Download file contents in parallel (with concurrency limit)

        Args:
            github_url: Public GitHub repository URL

        Returns:
            FetchResult with metadata, files, and skipped file list
        """
        owner, repo = self.parse_github_url(github_url)
        logger.info(f"Starting repository fetch: {owner}/{repo}")

        # Step 1: Detect branch
        branch = await self._detect_default_branch(owner, repo)

        # Step 2: Fetch tree
        tree_entries = await self._fetch_tree(owner, repo, branch)
        total_files = len(tree_entries)

        # Step 3: Filter files
        eligible_entries: list[dict] = []
        skipped_files: list[str] = []

        for entry in tree_entries:
            path = entry.get("path", "")
            size = entry.get("size", 0)

            if should_include_file(path, size, settings.max_file_size_kb):
                eligible_entries.append(entry)
            else:
                skipped_files.append(path)

        logger.info(
            f"File filter: {len(eligible_entries)} eligible, "
            f"{len(skipped_files)} skipped out of {total_files} total"
        )

        # Step 4: Download files in parallel with semaphore
        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_DOWNLOADS)
        files: list[RepoFile] = []

        async def _download_with_semaphore(entry: dict) -> RepoFile | None:
            async with semaphore:
                path = entry["path"]
                content = await self._download_file(owner, repo, path, branch)
                if content is not None:
                    return RepoFile(
                        path=path,
                        content=content,
                        size=entry.get("size", len(content)),
                        sha=entry.get("sha", ""),
                    )
                skipped_files.append(path)
                return None

        tasks = [_download_with_semaphore(entry) for entry in eligible_entries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, RepoFile):
                files.append(result)
            elif isinstance(result, Exception):
                logger.warning(f"Download task failed: {result}")

        logger.info(f"Successfully downloaded {len(files)} files")

        metadata = RepoMetadata(
            owner=owner,
            repo=repo,
            branch=branch,
            total_files_found=total_files,
            files_after_filter=len(files),
        )

        return FetchResult(
            metadata=metadata,
            files=files,
            skipped_files=skipped_files,
        )
