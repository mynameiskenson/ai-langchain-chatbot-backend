from enum import Enum

from sqlalchemy import Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base_model import BaseModel

class ConversationStatus(str, Enum):
    ARCHIVED = "ARCHIVED"
    ACTIVE = "ACTIVE"

class Conversation(BaseModel):
    __tablename__ = "conversations"

    status: Mapped[ConversationStatus] = mapped_column(
            SQLEnum(ConversationStatus),
            default=ConversationStatus.ACTIVE
        )
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    user_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)

