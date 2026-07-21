from app.common.repository.base import BaseRepository
from app.modules.message.models import Message
from sqlalchemy import select

class MessageRepository(BaseRepository[Message]):
    def __init__(self, db):
        super().__init__(db, Message)
    
    async def get_by_conversation(self, conversation_id: str, limit: int = 10, offset: int = 0) -> list[Message]:
        stmt = (
            select(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.scalars(stmt)
        return result.all()