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
    
    async def delete_by_document_id(self, document_id: str) -> None:
        stmt = select(DocumentChunk).filter(DocumentChunk.document_id == document_id)
        result = await self.db.scalars(stmt)
        chunks_to_delete = result.all()
        for chunk in chunks_to_delete:
            await self.db.delete(chunk)
        await self.db.commit()