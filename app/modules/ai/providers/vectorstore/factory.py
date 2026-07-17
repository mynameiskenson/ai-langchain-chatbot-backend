from typing import Callable

from app.uow.base import UnitOfWork
from app.modules.ai.constant import VectorDBProviderType
from app.modules.ai.providers.vectorstore.base import VectorStoreProvider
from app.modules.ai.providers.vectorstore.pgvector import PgVectorStore
from app.modules.ai.providers.vectorstore.qdrant import QdrantVectorStore
from app.modules.ai.providers.vectorstore.pinecone import PineconeVectorStore


class VectorStoreFactory:
    @staticmethod
    def create(provider: str, uow_factory: Callable[[], UnitOfWork]) -> VectorStoreProvider:
        provider = provider.lower()
        match provider:
            case VectorDBProviderType.PGVECTOR.value:
                return PgVectorStore(uow_factory=uow_factory)
            case VectorDBProviderType.QDRANT.value:
                return QdrantVectorStore()
            case VectorDBProviderType.PINECONE.value:
                return PineconeVectorStore()
            case _:
                raise ValueError(f"Unsupported vector store provider: {provider}")
