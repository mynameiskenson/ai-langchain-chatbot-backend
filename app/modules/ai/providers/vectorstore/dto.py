from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class VectorRecord:
    """A single chunk to be upserted into a vector store.

    `chunk_id` is the stable identifier used by the vector backend to
    reference this record (e.g. the `DocumentChunk.id` UUID primary key).
    """
    chunk_id: UUID
    document_id: UUID
    embedding: list[float]
    content: str
    chunk_index: int
    page_number: int | None
    metadata: dict


@dataclass(slots=True)
class VectorSearchResult:
    """A chunk returned from a vector store similarity search."""
    chunk_id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    page_number: int | None
    metadata: dict
    score: float | None = None
