from typing import Callable

from app.uow.base import UnitOfWork

from app.modules.ai.providers.embeddings.factory import EmbeddingFactory
from app.modules.ai.providers.embeddings.base import EmbeddingProvider

from app.modules.ai.retrieval.dto import RetrievedChunk

class RetrievalService:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        embedding_provider: EmbeddingProvider | None = None,
        provider_name: str | None = None,
    ):
        """Create a retrieval service.

        Pass `embedding_provider` or `provider_name` to set the embedding backend.
        """
        self.uow_factory = uow_factory

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

        # Perform similarity search in the database
        async with self.uow_factory() as uow:
            chunks = await uow.retrieval_chunks.similarity_search(query_embedding, top_k=top_k)

        # Convert the retrieved chunks to RetrievedChunk DTOs
        return [RetrievedChunk(
            document_id=chunk.document_id,
            content=chunk.content,
            chunk_index=chunk.chunk_index,
            page_number=chunk.page_number,
            metadata=chunk.metadata,
            score=chunk.score,
        ) for chunk in chunks]