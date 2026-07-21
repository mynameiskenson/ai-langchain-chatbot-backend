from sqlalchemy.ext.asyncio import AsyncSession

from app.uow.base import UnitOfWork
from app.modules.conversation.repository import ConversationRepository
from app.modules.document.repository import DocumentChunkRepository, DocumentRepository
from app.modules.ai.retrieval.repository import RetrievalChunkRepository
from app.modules.message.repository import MessageRepository


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session
        
        # repositories bound to the same session
        self.conversations = ConversationRepository(self.session)
        self.documents = DocumentRepository(self.session)
        self.document_chunks = DocumentChunkRepository(self.session)
        self.retrieval_chunks = RetrievalChunkRepository(self.session)
        self.messages = MessageRepository(self.session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def close(self):
        await self.session.close()
