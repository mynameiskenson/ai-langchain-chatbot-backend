from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum

from sqlalchemy import Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.modules.message.models import Message

class ConversationStatus(str, Enum):
    ARCHIVED = "ARCHIVED"
    ACTIVE = "ACTIVE"

class Conversation(BaseModel):
    __tablename__ = "conversations"

    status: Mapped[ConversationStatus] = mapped_column(
            SQLEnum(ConversationStatus),
            default=ConversationStatus.ACTIVE
        )
    
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    user_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
