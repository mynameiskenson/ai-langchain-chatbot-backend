from typing import Callable

from app.uow.base import UnitOfWork
from app.core.exceptions import NotFoundException, ValidationException

from app.modules.conversation.models import Conversation


class ConversationService:
    def __init__(self, uow_factory: Callable[[], UnitOfWork]):
        """Initialize ConversationService with a unit-of-work factory."""
        self.uow_factory = uow_factory

    async def _with_uow(self, uow: UnitOfWork | None, func):
        """Run `func(uow)` using the given `uow` if provided (caller manages its
        lifecycle/commit), otherwise open and manage a new one.
        """
        if uow is not None:
            return await func(uow)
        async with self.uow_factory() as uow:
            return await func(uow)

    async def create_conversation(self, title: str, user_id: str, uow: UnitOfWork | None = None):
        if title is None or title.strip() == "":
            raise ValidationException("Conversation title cannot be empty.")
        if user_id is None or user_id.strip() == "":
            raise ValidationException("User ID cannot be empty.")

        async def _op(uow: UnitOfWork):
            convo = Conversation(title=title, user_id=user_id)
            return await uow.conversations.create(convo)

        return await self._with_uow(uow, _op)

    async def get_conversation(self, conversation_id: str, uow: UnitOfWork | None = None):
        async def _op(uow: UnitOfWork):
            entity = await uow.conversations.get(conversation_id)
            if entity is None:
                raise NotFoundException(f"Conversation '{conversation_id}' not found.")
            return entity

        return await self._with_uow(uow, _op)

    async def get_conversations_by_user(self, user_id: str, uow: UnitOfWork | None = None):
        if not user_id or user_id.strip() == "":
            raise ValidationException("User ID cannot be empty.")

        async def _op(uow: UnitOfWork):
            result = await uow.conversations.get_conversations_by_user(user_id)
            if not result:
                raise NotFoundException(f"No conversations found for user '{user_id}'.")
            return result

        return await self._with_uow(uow, _op)

    async def update_conversation(self, conversation_id: str, title: str = None, uow: UnitOfWork | None = None):
        async def _op(uow: UnitOfWork):
            entity = await uow.conversations.get(conversation_id)
            if entity is None:
                raise NotFoundException(f"Conversation '{conversation_id}' not found.")
            return await uow.conversations.update(entity, {"title": title})

        return await self._with_uow(uow, _op)

    async def archive_conversation(self, conversation_id: str, uow: UnitOfWork | None = None):
        async def _op(uow: UnitOfWork):
            entity = await uow.conversations.get(conversation_id)
            if entity is None:
                raise NotFoundException(f"Conversation '{conversation_id}' not found.")
            return await uow.conversations.update(entity, {"status": "ARCHIVED"})

        return await self._with_uow(uow, _op)