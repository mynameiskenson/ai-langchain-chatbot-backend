from dataclasses import dataclass
from uuid import UUID

@dataclass(slots=True)
class RetrievedChunk:
    """A chunk returned from retrieval.

    Fields:
    - document_id: source document UUID
    - content: chunk text
    - chunk_index: index within the document
    - page_number: page number or None
    - metadata: metadata dict
    - score: relevance score or None
    """
    document_id: UUID
    content: str
    chunk_index: int
    metadata: dict
    page_number: int | None
    score: float | None = None