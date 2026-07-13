from abc import ABC, abstractmethod

class EmbeddingProvider(ABC):
    """Abstract base class for embeddings providers."""

    @abstractmethod
    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Embed a list of documents."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        """Embed a single query."""
        pass