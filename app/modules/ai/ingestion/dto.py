from dataclasses import dataclass
from app.modules.ai.providers.embeddings.dto import Embedding

@dataclass(slots=True)
class Chunk:
    """A piece of a document used during ingestion.

    Fields:
    - content: chunk text
    - chunk_index: index within the document
    - page_number: page number or None
    - metadata: additional metadata dict
    - embedding: optional Embedding object
    """
    content: str
    chunk_index: int
    metadata: dict
    page_number: int | None
    embedding: Embedding | None = None
