from typing import Callable

from app.uow.base import UnitOfWork
from app.core.exceptions import NotFoundException, ValidationException

from app.modules.conversation.models import Conversation


class ConversationService:
    def __init__(self, uow_factory: Callable[[], UnitOfWork]):
        """uow_factory should be a zero-arg callable returning an async context manager
        that yields a UnitOfWork (for example `get_uow`)."""
        self.uow_factory = uow_factory

    async def create_conversation(self, title: str, owner_id: str):
        if title is None or title.strip() == "":
            raise ValidationException("Conversation title cannot be empty.")
        if owner_id is None or owner_id.strip() == "":
            raise ValidationException("Owner ID cannot be empty.")
        async with self.uow_factory() as uow:
            convo = Conversation(title=title, owner_id=owner_id)
            return await uow.conversations.create(convo)

    async def get_conversation(self, conversation_id: str):
        async with self.uow_factory() as uow:
            entity = await uow.conversations.get(conversation_id)
            if entity is None:
                raise NotFoundException(f"Conversation '{conversation_id}' not found.")
            return entity
        
    async def get_conversations_by_owner(self, owner_id: str):
        if not owner_id or owner_id.strip() == "":
            raise ValidationException("Owner ID cannot be empty.")
        async with self.uow_factory() as uow:
            result = await uow.conversations.get_conversations_by_owner(owner_id)
            if not result:
                raise NotFoundException(f"No conversations found for owner '{owner_id}'.")
            return result

    async def update_conversation(self, conversation_id: str, title: str = None):
        async with self.uow_factory() as uow:
            entity = await uow.conversations.get(conversation_id)
            if entity is None:
                raise NotFoundException(f"Conversation '{conversation_id}' not found.")
            return await uow.conversations.update(entity, {"title": title})

    async def archive_conversation(self, conversation_id: str):
        async with self.uow_factory() as uow:
            entity = await uow.conversations.get(conversation_id)
            if entity is None:
                raise NotFoundException(f"Conversation '{conversation_id}' not found.")
            return await uow.conversations.update(entity, {"status": "ARCHIVED"})