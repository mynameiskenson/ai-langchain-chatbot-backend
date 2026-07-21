from datetime import datetime, timezone

from app.common.repository.base import BaseRepository
from app.modules.document.models import Document
from sqlalchemy import select

class DocumentRepository(BaseRepository[Document]):
    def __init__(self, db):
        super().__init__(db, Document)
    
    async def get_document_by_user(self, user_id: str) -> list[Document]:
        stmt = select(Document).filter(Document.user_id == user_id)
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
            chunk.is_deleted = True
            chunk.deleted_at = datetime.now(timezone.utc)
            chunk.deleted_by = "system"  # or use doc.user_id if you want to track the user who deleted it

        await self.db.commit()