from abc import ABC, abstractmethod

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.modules.ai.ingestion.dto import Chunk
from app.core.config import settings

class TextSplitter(ABC):
    """Base class for text splitting implementations."""

    @abstractmethod
    async def split(self, document: list[Document]) -> list[Chunk]:
        """Split documents into `Chunk` objects."""
        pass

class RecursiveTextSplitter(TextSplitter):
    """Split text using a recursive character splitter."""

    def __init__(self, chunk_size: int = settings.ai.CHUNKSIZE, chunk_overlap: int = settings.ai.CHUNK_OVERLAP):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    async def split(self, documents: list[Document]) -> list[Chunk]:
        """Return a list of `Chunk` for the provided documents."""
        chunks = []
        for doc in documents:
            split_texts = self.splitter.split_text(doc.page_content)
            for index, text in enumerate(split_texts):
                chunk = Chunk(
                    content=text,
                    chunk_index=index,
                    page_number=doc.metadata.get("page_number"),
                    metadata=doc.metadata
                )
                chunks.append(chunk)
        return chunks