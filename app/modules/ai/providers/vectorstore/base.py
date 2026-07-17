from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.ai.providers.vectorstore.dto import VectorRecord, VectorSearchResult


class VectorStoreProvider(ABC):
    """Base class for vector store providers (pgvector, Qdrant, Pinecone, ...).

    Implementations are responsible for storing embeddings (plus a copy of the
    chunk content/metadata) and performing similarity search. Relational
    bookkeeping of `Document`/`DocumentChunk` rows (status, content, lifecycle)
    stays in the primary relational database regardless of which vector
    backend is active.
    """

    @abstractmethod
    async def upsert(self, records: list[VectorRecord]) -> None:
        """Insert or update embeddings (and their content/metadata) for the given records."""
        pass

    @abstractmethod
    async def search(self, query_embedding: list[float], top_k: int = 5, filters: dict | None = None) -> list[VectorSearchResult]:
        """Return the top_k most similar records to the query embedding."""
        pass

    @abstractmethod
    async def delete_by_document(self, document_id: UUID) -> None:
        """Remove all vectors associated with a document."""
        pass
