"""
Embedding Service — generates text embeddings using Google Gemini's gemini-embedding-002 model.

Features:
- Thread-safe / Async batching of text chunks
- Robust rate limit handling and exponential backoff
- Performance tracking (calculates time taken to generate embeddings)
"""

import asyncio
import time
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import EmbeddingError


class EmbeddingService:
    """Generates vector embeddings for code chunks using the Google Gemini API."""

    def __init__(self):
        if not settings.google_api_key or settings.google_api_key == "your_google_api_key_here":
            raise EmbeddingError(
                message="Google API key is not configured",
                details="Please set GOOGLE_API_KEY in your environment or .env file."
            )

        logger.info(f"Initializing Gemini Embeddings with model: {settings.gemini_embedding_model}")
        
        # Instantiate LangChain's Google Generative AI Embeddings
        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.gemini_embedding_model,
            google_api_key=settings.google_api_key,
        )

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=15),
        reraise=True,
    )
    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a single batch of texts with retry logic.
        Synchronous wrapper for LangChain call.
        """
        try:
            return self._embeddings.embed_documents(texts)
        except Exception as e:
            logger.warning(f"Gemini embedding batch failed: {e}. Retrying...")
            raise

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of texts.
        Splits the texts into batches to comply with payload sizes and rate limits.

        Args:
            texts: List of strings to embed

        Returns:
            List of embedding vectors (each 3072-dimensional)
        """
        if not texts:
            return []

        batch_size = settings.embedding_batch_size
        batches = [texts[i : i + batch_size] for i in range(0, len(texts), batch_size)]
        
        all_embeddings: list[list[float]] = []
        logger.info(f"Generating embeddings for {len(texts)} chunks in {len(batches)} batches")

        loop = asyncio.get_running_loop()

        for idx, batch in enumerate(batches):
            try:
                # Run the synchronous embedding call in an executor to avoid blocking the event loop
                start_time = time.time()
                vectors = await loop.run_in_executor(None, self._embed_batch, batch)
                duration = time.time() - start_time
                
                logger.debug(f"Embedded batch {idx + 1}/{len(batches)} ({len(batch)} items) in {duration:.2f}s")
                all_embeddings.extend(vectors)

                # Simple throttle for Gemini free-tier rate limits (1500 RPM for embeddings)
                if idx < len(batches) - 1:
                    await asyncio.sleep(0.1)

            except Exception as e:
                raise EmbeddingError(
                    message=f"Failed to generate embeddings at batch {idx + 1}",
                    details=str(e)
                )

        logger.info(f"Successfully generated {len(all_embeddings)} embeddings")
        return all_embeddings

    async def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding for a single user query.
        """
        try:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                None, self._embeddings.embed_query, query
            )
        except Exception as e:
            raise EmbeddingError(
                message="Failed to generate query embedding",
                details=str(e)
            )
