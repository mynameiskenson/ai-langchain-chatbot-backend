from app.common.repository.base import BaseRepository
from app.modules.conversation.models import Conversation
from sqlalchemy import select

class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, db):
        super().__init__(db, Conversation)

    async def get_conversations_by_user(self, user_id: str, limit: int = 10) -> list[Conversation]:
        stmt = select(Conversation).filter(Conversation.user_id == user_id).limit(limit)
        result = await self.db.scalars(stmt)
        return result.all()