from app.common.repository.base import BaseRepository
from app.modules.document.models import Document
from sqlalchemy import select

class DocumentRepository(BaseRepository[Document]):
    def __init__(self, db):
        super().__init__(db, Document)
    
    async def get_document_by_owner(self, owner_id: str) -> list[Document]:
        stmt = select(Document).filter(Document.owner_id == owner_id)
        result = await self.db.scalars(stmt)
        return result.all()
    
from app.modules.document.models import DocumentChunk

class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    def __init__(self, db):
        super().__init__(db, DocumentChunk)
    
    async def create_many(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        self.db.add_all(chunks)
        await self.db.flush()
        for chunk in chunks:
            await self.db.refresh(chunk)
        return chunks
    
    async def similarity_search(self, query_embedding: list[float], top_k: int = 5) -> list[DocumentChunk]:
        stmt = select(DocumentChunk).order_by(DocumentChunk.embedding.cosine_distance(query_embedding)).limit(top_k)
        result = await self.db.scalars(stmt)
        return result.all()
    
    async def delete_by_document_id(self, document_id: str) -> None:
        stmt = select(DocumentChunk).filter(DocumentChunk.document_id == document_id)
        result = await self.db.scalars(stmt)
        chunks_to_delete = result.all()
        for chunk in chunks_to_delete:
            await self.db.delete(chunk)
        await self.db.commit()