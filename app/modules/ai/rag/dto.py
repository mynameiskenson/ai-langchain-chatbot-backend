from dataclasses import dataclass

from app.modules.ai.providers.llm.dto import ChatResponse
from app.modules.ai.retrieval.dto import RetrievedChunk

@dataclass(slots=True)
class RAGRequest:
    """Request for retrieval-augmented generation (RAG).

    Fields:
    - query: the user's question or search text
    - owner_id: optional owner identifier
    - top_k: how many top chunks to retrieve
    """
    query: str
    owner_id: str | None = None
    top_k: int

@dataclass(slots=True)
class RAGResponse:
    """Response from RAG containing the LLM response and the retrieved chunks.

    Fields:
    - response: the LLM's `ChatResponse` DTO
    - retrieved_chunks: list of `RetrievedChunk` DTOs
    """
    response: ChatResponse
    retrieved_chunks: list[RetrievedChunk]