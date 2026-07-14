from langchain_ollama import OllamaEmbeddings

from app.core.config import settings
from app.modules.ai.providers.embeddings.base import EmbeddingProvider

class OllamaEmbeddingProvider(EmbeddingProvider):
    """Embedding provider implementation using Ollama."""

    def __init__(self):
        self.model = settings.ai.EMBEDDING_MODEL
        self.dimension = settings.ai.EMBEDDING_DIMENSION
        self.embeddings = OllamaEmbeddings(model=self.model)

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Return embeddings for multiple documents."""
        return self.embeddings.embed_documents(documents)

    def embed_query(self, query: str) -> list[float]:
        """Return an embedding for a single query."""
        return self.embeddings.embed_query(query)