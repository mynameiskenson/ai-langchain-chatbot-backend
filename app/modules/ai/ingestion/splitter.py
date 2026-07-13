from abc import ABC, abstractmethod

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.modules.ai.ingestion.dto import Chunk
from app.core.config import settings

class TextSplitter(ABC):
    """Abstract base class for text splitters."""

    @abstractmethod
    def split(self, document: list[Document]) -> list[Chunk]:
        """Split a document into chunks."""
        pass

class RecursiveTextSplitter(TextSplitter):
    """Concrete implementation of TextSplitter using RecursiveCharacterTextSplitter."""

    def __init__(self, chunk_size: int = settings.ai.CHUNKSIZE, chunk_overlap: int = settings.ai.CHUNK_OVERLAP):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def split(self, documents: list[Document]) -> list[Chunk]:
        """Split documents into chunks."""
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