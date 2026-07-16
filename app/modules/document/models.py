from enum import Enum
from uuid import UUID

from sqlalchemy import Enum as SQLEnum, String, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from pgvector.sqlalchemy import Vector

from app.core.config import settings
from app.database.models.base_model import BaseModel

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    DELETED = "deleted"

class Document(BaseModel):
    __tablename__ = "documents"

    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(DocumentStatus),
        default=DocumentStatus.UPLOADED
    )

    user_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)

    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)

    file_size: Mapped[int] = mapped_column(nullable=False)

    storage_provider: Mapped[str] = mapped_column(String(255), nullable=False)

    storage_path: Mapped[str] = mapped_column(String(255), nullable=False)

    chunks: Mapped[list["DocumentChunk"]] = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    
class DocumentChunk(BaseModel):
    __tablename__ = "document_chunks"

    document_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    content_hash: Mapped[str] = mapped_column(String(64))

    embedding: Mapped[list[float]] = mapped_column(Vector(settings.ai.EMBEDDING_DIMENSION), nullable=False)

    chunk_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    embedding_model: Mapped[str] = mapped_column(String(255), nullable=False, default=settings.ai.EMBEDDING_MODEL)





