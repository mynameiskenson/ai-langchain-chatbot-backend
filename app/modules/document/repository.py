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