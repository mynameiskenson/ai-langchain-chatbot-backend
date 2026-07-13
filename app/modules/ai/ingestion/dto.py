from dataclasses import dataclass
from app.modules.ai.providers.embeddings.dto import Embedding

@dataclass(slots=True)
class Chunk:
    """
    Represents a chunk of data for ingestion.

    Attributes:
        content (str): The actual content of the chunk.
        chunk_index (int): The index of the chunk within the document.
        page_number (int | None): The page number of the chunk, if applicable.
        metadata (dict): Additional metadata associated with the chunk.
    """
    content: str
    chunk_index: int
    page_number: int | None
    metadata: dict
    embedding: Embedding | None = None
