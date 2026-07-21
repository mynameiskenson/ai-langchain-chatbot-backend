from __future__ import annotations
from uuid import UUID
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID

from app.database.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.modules.conversation.models import Conversation

class Message(BaseModel):
    __tablename__ = "messages"

    conversation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    content: Mapped[str] = mapped_column(String(2048), nullable=False)

    role: Mapped[str] = mapped_column(String(50), nullable=False)