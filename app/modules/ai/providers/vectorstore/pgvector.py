from typing import Callable
from uuid import UUID

from app.uow.base import UnitOfWork
from app.modules.ai.providers.vectorstore.base import VectorStoreProvider
from app.modules.ai.providers.vectorstore.dto import VectorRecord, VectorSearchResult


class PgVectorStore(VectorStoreProvider):
    """Vector store backed by the pgvector extension on the primary Postgres database.

    Chunk content/metadata already lives in the `document_chunks` table (written
    by the relational repositories during ingestion); this provider only needs
    to populate/query the `embedding` column on those same rows.
    """

    def __init__(self, uow_factory: Callable[[], UnitOfWork]):
        self.uow_factory = uow_factory

    async def upsert(self, records: list[VectorRecord]) -> None:
        async with self.uow_factory() as uow:
            for record in records:
                chunk = await uow.document_chunks.get(record.chunk_id)
                if chunk is None:
                    continue
                await uow.document_chunks.update(chunk, {"embedding": record.embedding})

    async def search(self, query_embedding: list[float], top_k: int = 5, filters: dict | None = None) -> list[VectorSearchResult]:
        async with self.uow_factory() as uow:
            chunks = await uow.retrieval_chunks.similarity_search(query_embedding, top_k=top_k)

        return [
            VectorSearchResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                page_number=chunk.page_number,
                metadata=chunk.chunk_metadata,
                score=getattr(chunk, "score", None),
            )
            for chunk in chunks
        ]

    async def delete_by_document(self, document_id: UUID) -> None:
        async with self.uow_factory() as uow:
            await uow.document_chunks.delete_by_document_id(str(document_id))
