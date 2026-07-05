"""
RAG Service — orchestrates the retrieval-augmented generation query pipeline.

Coordinates:
1. Question embedding generation (Gemini)
2. Semantic similarity retrieval (Pinecone)
3. Prompt engineering with source context
4. Codebase-specific response generation (Gemini 2.0 Flash)
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import RAGQueryError
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.models.responses import ChatResponse, SourceChunk


class RAGService:
    """Manages semantic codebase queries and LLM answer generation."""

    SYSTEM_PROMPT = """You are a senior AI software engineer and system architect.
Your task is to answer user questions about a software repository using the provided source code context.

Guidelines:
1. Use only the provided code snippets in the context to construct your answer.
2. If the context is empty or does not contain enough information to answer the question, state that you cannot find the answer in the ingested codebase. Do not hallucinate or make up code.
3. Be highly technical, precise, and direct. Show code examples or walk through logic when requested.
4. When referencing files, always cite the full file path and line numbers (e.g., `src/auth/service.py#L42-50`).
5. Format your response cleanly in Markdown. Wrap code blocks in triple backticks with the correct language syntax highlighting (e.g. ```python).
"""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStoreService,
    ):
        self._embedding_service = embedding_service
        self._vector_store = vector_store
        
        if not settings.google_api_key or settings.google_api_key == "your_google_api_key_here":
            raise RAGQueryError(
                message="Google API key is not configured",
                details="Please set GOOGLE_API_KEY in your environment or .env file."
            )

        logger.info(f"Initializing Gemini Chat LLM with model: {settings.gemini_chat_model}")
        
        # Instantiate LangChain's Google Generative AI LLM client
        self._llm = ChatGoogleGenerativeAI(
            model=settings.gemini_chat_model,
            google_api_key=settings.google_api_key,
            temperature=0.1,  # Low temperature for factual, codebase-grounded answers
        )

    def _build_context_string(self, matches: list[dict]) -> str:
        """Format matching database records into a single structured context string."""
        context_parts = []
        for idx, match in enumerate(matches):
            meta = match.get("metadata", {})
            file_path = meta.get("file_path", "unknown_file")
            start_line = int(meta.get("start_line", 0))
            end_line = int(meta.get("end_line", 0))
            language = meta.get("language", "text")
            imports = meta.get("imports", "")
            parent_context = meta.get("parent_context", "")
            text_content = meta.get("text", "")

            part = f"--- SOURCE BLOCK {idx + 1} ---\n"
            part += f"File: {file_path} (Lines: {start_line}-{end_line}, Language: {language})\n"
            if parent_context:
                part += f"Enclosing Scope: {parent_context}\n"
            if imports:
                part += f"Top-level Imports: {imports}\n"
            part += f"Code Snippet:\n{text_content}\n"
            context_parts.append(part)

        return "\n\n".join(context_parts)

    async def answer_question(
        self,
        repository_id: str,
        question: str,
        top_k: int = settings.top_k,
    ) -> ChatResponse:
        """
        Runs the complete RAG Q&A pipeline.

        Args:
            repository_id: Repository namespace in Pinecone (owner_repo)
            question: Natural language question from user
            top_k: Number of semantic sources to retrieve

        Returns:
            ChatResponse with LLM answer and retrieved source chunks
        """
        logger.info(f"Querying repository '{repository_id}' for question: {question[:80]}...")

        try:
            # Step 1: Generate vector embedding of the user's question
            query_vector = await self._embedding_service.embed_query(question)

            # Step 2: Query vector store for similar code chunks
            matches = await self._vector_store.similarity_search(
                query_vector=query_vector,
                namespace=repository_id,
                top_k=top_k,
            )

            if not matches:
                return ChatResponse(
                    answer=(
                        "I couldn't find any code chunks matching your question in the database. "
                        "Make sure the repository has been ingested successfully."
                    ),
                    sources=[]
                )

            # Step 3: Format sources list for the response model
            sources = []
            for match in matches:
                meta = match.get("metadata", {})
                sources.append(
                    SourceChunk(
                        file_path=meta.get("file_path", "unknown"),
                        start_line=meta.get("start_line"),
                        end_line=meta.get("end_line"),
                        snippet=meta.get("text", ""),
                        relevance_score=float(match.get("score", 0.0)),
                    )
                )

            # Step 4: Build prompt messages
            context_str = self._build_context_string(matches)
            
            user_message_content = f"""Codebase Context:
{context_str}

User Question: {question}

Answer:"""

            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=user_message_content),
            ]

            # Step 5: Ask Gemini for completion
            logger.info("Sending prompt to Gemini LLM")
            response = await self._llm.ainvoke(messages)
            answer = str(response.content)

            return ChatResponse(answer=answer, sources=sources)

        except Exception as e:
            logger.error(f"RAG query execution failed: {e}", exc_info=True)
            raise RAGQueryError(
                message="RAG query processing failed",
                details=str(e)
            )
