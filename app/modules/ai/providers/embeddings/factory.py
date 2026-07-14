from app.modules.ai.constant import AIProviderType

from app.modules.ai.providers.embeddings.ollama import OllamaEmbeddingProvider
from app.modules.ai.providers.embeddings.base import EmbeddingProvider
from app.core.config import settings

class EmbeddingFactory:
    @staticmethod
    def create(provider: str) -> EmbeddingProvider:
        provider = provider.lower()
        match provider:
            case AIProviderType.OLLAMA.value:
                return OllamaEmbeddingProvider()
            case _:
                raise ValueError(f"Unsupported embedding provider: {provider}")