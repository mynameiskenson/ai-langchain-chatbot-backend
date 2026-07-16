from langchain_ollama import OllamaEmbeddings

from app.core.config import settings
from app.modules.ai.providers.embeddings.base import EmbeddingProvider

class OllamaEmbeddingProvider(EmbeddingProvider):
    """Embedding provider implementation using Ollama."""

    def __init__(self):
        self.model = settings.ai.EMBEDDING_MODEL
        self.dimension = settings.ai.EMBEDDING_DIMENSION
        self.embeddings = OllamaEmbeddings(model=self.model)

    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Return embeddings for multiple documents."""
        return await self.embeddings.aembed_documents(documents)

    async def embed_query(self, query: str) -> list[float]:
        """Return an embedding for a single query."""
        return await self.embeddings.aembed_query(query)