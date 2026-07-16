from abc import ABC, abstractmethod

class EmbeddingProvider(ABC):
    """Base class for embedding providers."""

    @abstractmethod
    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Return embedding vectors for a list of texts."""
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> list[float]:
        """Return an embedding vector for a query string."""
        pass