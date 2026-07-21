from typing import Callable

from app.uow.base import UnitOfWork
from app.modules.message.models import Message
from app.modules.ai.providers.llm.dto import ChatMessage

class MessageService:
    def __init__(self, uow_factory: Callable[[], UnitOfWork]):
        """Initialize MessageService with a unit-of-work factory."""
        self.uow_factory = uow_factory

    async def _with_uow(self, uow: UnitOfWork | None, func):
        """Run `func(uow)` using the given `uow` if provided (caller manages its
        lifecycle/commit), otherwise open and manage a new one.
        """
        if uow is not None:
            return await func(uow)
        async with self.uow_factory() as uow:
            return await func(uow)

    async def append_message(self, conversation_id: str, role: str, content: str, uow: UnitOfWork | None = None) -> Message:
        if not conversation_id or conversation_id.strip() == "":
            raise ValueError("Conversation ID cannot be empty.")
        if not role or role.strip() == "":
            raise ValueError("Role cannot be empty.")
        if not content or content.strip() == "":
            raise ValueError("Content cannot be empty.")

        async def _op(uow: UnitOfWork):
            message = Message(conversation_id=conversation_id, role=role, content=content)
            return await uow.messages.create(message)

        return await self._with_uow(uow, _op)

    async def get_history(self, conversation_id: str, limit: int = 10, uow: UnitOfWork | None = None) -> list[ChatMessage]:
        if not conversation_id or conversation_id.strip() == "":
            raise ValueError("Conversation ID cannot be empty.")

        async def _op(uow: UnitOfWork):
            messages = await uow.messages.get_by_conversation(conversation_id, limit=limit)
            return [ChatMessage(role=msg.role, content=msg.content) for msg in messages]

        return await self._with_uow(uow, _op)