"""
Vector Store Service — manages Pinecone vector database operations.

Features:
- Automated index creation (3072 dimensions, cosine metric, AWS us-east-1 serverless starter index)
- Namespace management (isolated namespaces per repository ID)
- Bulk upserting (upserts in batches of 100 vectors)
- Namespace clearing (resets index state for re-ingestion)
- Metadata-filtered similarity searches
"""

from typing import Any
import asyncio
from pinecone import Pinecone, ServerlessSpec
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import VectorStoreError
from app.services.chunking_service import CodeChunk


class VectorStoreService:
    """Manages all Pinecone vector database data and control plane operations."""

    def __init__(self):
        if not settings.pinecone_api_key or settings.pinecone_api_key == "your_pinecone_api_key_here":
            raise VectorStoreError(
                message="Pinecone API key is not configured",
                details="Please set PINECONE_API_KEY in your environment or .env file."
            )

        try:
            logger.info("Initializing Pinecone client")
            self._pc = Pinecone(api_key=settings.pinecone_api_key)
            self._index_name = settings.pinecone_index
            self._ensure_index_exists()
            self._index = self._pc.Index(self._index_name)
        except Exception as e:
            raise VectorStoreError(
                message="Failed to initialize Pinecone client or index",
                details=str(e)
            )

    def _ensure_index_exists(self):
        """Creates the index if it does not exist in the Pinecone account."""
        try:
            # Check if index exists in the list of names
            existing_indexes = [idx.name for idx in self._pc.list_indexes()]
            if self._index_name not in existing_indexes:
                logger.info(f"Pinecone index '{self._index_name}' does not exist. Creating...")
                
                self._pc.create_index(
                    name=self._index_name,
                    dimension=settings.embedding_dimensions,  # 3072 for Gemini
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"  # Free tier serverless region
                    )
                )
                logger.info(f"Pinecone index '{self._index_name}' created successfully")
            else:
                logger.debug(f"Pinecone index '{self._index_name}' already exists")
        except Exception as e:
            raise VectorStoreError(
                message="Failed to verify or create Pinecone index",
                details=str(e)
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _delete_namespace_sync(self, namespace: str):
        """Synchronously clears vectors inside a namespace."""
        try:
            # Check if namespace exists by describing index statistics
            stats = self._index.describe_index_stats()
            if namespace in stats.get("namespaces", {}):
                logger.info(f"Clearing existing vectors in namespace: '{namespace}'")
                self._index.delete(delete_all=True, namespace=namespace)
        except Exception as e:
            logger.warning(f"Failed to delete namespace '{namespace}': {e}")
            raise

    async def clear_namespace(self, namespace: str):
        """Asynchronously clears a namespace before ingestion."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._delete_namespace_sync, namespace)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _upsert_batch_sync(self, batch: list[tuple[str, list[float], dict[str, Any]]], namespace: str):
        """Synchronously upserts a single batch of vectors."""
        try:
            self._index.upsert(vectors=batch, namespace=namespace)
        except Exception as e:
            logger.warning(f"Pinecone upsert batch failed: {e}. Retrying...")
            raise

    async def upsert_chunks(
        self,
        chunks: list[CodeChunk],
        embeddings: list[list[float]],
        namespace: str,
    ):
        """
        Upsert chunks and their generated embeddings into Pinecone in batches.

        Args:
            chunks: List of CodeChunk objects
            embeddings: List of embedding vectors
            namespace: Destination namespace in Pinecone (usually owner_repo format)
        """
        if len(chunks) != len(embeddings):
            raise VectorStoreError(
                message="Mismatch between chunk count and embedding count",
                details=f"Chunks: {len(chunks)}, Embeddings: {len(embeddings)}"
            )

        if not chunks:
            logger.info("No chunks to upsert")
            return

        # Prepare records: (id, vector, metadata)
        records = []
        for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            # ID format: path_chunkindex
            record_id = f"{chunk.metadata['file_path']}_{chunk.metadata['chunk_index']}"
            # Pinecone metadata must only contain simple types (string, number, boolean, list of strings)
            # Make sure metadata matches this structure
            meta = {**chunk.metadata, "text": chunk.content}
            records.append((record_id, vector, meta))

        # Bulk upsert in batches of 100
        batch_size = 100
        batches = [records[i : i + batch_size] for i in range(0, len(records), batch_size)]
        
        logger.info(f"Upserting {len(records)} records into namespace '{namespace}' in {len(batches)} batches")
        loop = asyncio.get_running_loop()

        for idx, batch in enumerate(batches):
            try:
                await loop.run_in_executor(None, self._upsert_batch_sync, batch, namespace)
                logger.debug(f"Upserted batch {idx + 1}/{len(batches)} ({len(batch)} items)")
            except Exception as e:
                raise VectorStoreError(
                    message=f"Failed to upsert batch {idx + 1} to Pinecone",
                    details=str(e)
                )

        logger.info(f"Successfully upserted all chunks to Pinecone namespace '{namespace}'")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
    )
    def _query_sync(self, vector: list[float], namespace: str, top_k: int) -> dict[str, Any]:
        """Synchronously query the Pinecone index."""
        try:
            return self._index.query(
                namespace=namespace,
                vector=vector,
                top_k=top_k,
                include_metadata=True,
            )
        except Exception as e:
            logger.warning(f"Pinecone query failed: {e}. Retrying...")
            raise

    async def similarity_search(
        self,
        query_vector: list[float],
        namespace: str,
        top_k: int = settings.top_k,
    ) -> list[dict[str, Any]]:
        """
        Performs similarity search in a namespace.

        Args:
            query_vector: The query's embedding vector
            namespace: Namespace to search in
            top_k: Top-k matches to return

        Returns:
            List of matched documents with scores and metadata
        """
        logger.info(f"Performing similarity search in namespace '{namespace}' (top_k={top_k})")
        loop = asyncio.get_running_loop()

        try:
            response = await loop.run_in_executor(
                None, self._query_sync, query_vector, namespace, top_k
            )
            matches = response.get("matches", [])
            logger.info(f"Found {len(matches)} matches in vector store")
            return matches
        except Exception as e:
            raise VectorStoreError(
                message="Similarity search in Pinecone failed",
                details=str(e)
            )
