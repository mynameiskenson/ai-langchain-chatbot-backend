from typing import Callable

from app.uow.base import UnitOfWork

from app.modules.ai.providers.embeddings.factory import EmbeddingFactory
from app.modules.ai.providers.embeddings.base import EmbeddingProvider

from app.modules.ai.providers.vectorstore.base import VectorStoreProvider

from app.modules.ai.retrieval.dto import RetrievedChunk

class RetrievalService:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        vector_store: VectorStoreProvider,
        embedding_provider: EmbeddingProvider | None = None,
        provider_name: str | None = None,
    ):
        """Create a retrieval service.

        Pass `embedding_provider` or `provider_name` to set the embedding backend.
        `vector_store` is the pluggable backend (pgvector/Qdrant/Pinecone) used
        for similarity search.
        """
        self.uow_factory = uow_factory
        self.vector_store = vector_store

        if provider_name is not None:
            self.embedding_provider = EmbeddingFactory.create(provider_name)
        else:
            self.embedding_provider = embedding_provider

    async def semantic_search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Return the top_k most similar chunks for the query."""
        if not self.embedding_provider:
            raise ValueError("No embedding provider is configured.")

        # Compute the embedding for the query
        query_embedding = await self.embedding_provider.embed_query(query)

        # Perform similarity search via the configured vector store
        results = await self.vector_store.search(query_embedding, top_k=top_k)

        # Convert the retrieved results to RetrievedChunk DTOs
        return [RetrievedChunk(
            document_id=result.document_id,
            content=result.content,
            chunk_index=result.chunk_index,
            page_number=result.page_number,
            metadata=result.metadata,
            score=result.score,
        ) for result in results]