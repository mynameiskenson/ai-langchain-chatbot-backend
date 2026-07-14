from abc import ABC, abstractmethod

class EmbeddingProvider(ABC):
    """Base class for embedding providers."""

    @abstractmethod
    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Return embedding vectors for a list of texts."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        """Return an embedding vector for a query string."""
        pass