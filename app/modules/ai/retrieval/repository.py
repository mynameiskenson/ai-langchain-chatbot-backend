from sqlalchemy import select

from app.common.repository.base import BaseRepository

from app.modules.document.models import DocumentChunk

class RetrievalChunkRepository(BaseRepository[DocumentChunk]):
    def __init__(self, db):
        super().__init__(db, DocumentChunk)

    async def similarity_search(self, query_embedding: list[float], top_k: int = 5) -> list[DocumentChunk]:
        stmt = select(DocumentChunk).order_by(DocumentChunk.embedding.cosine_distance(query_embedding)).limit(top_k)
        result = await self.db.scalars(stmt)
        return result.all()