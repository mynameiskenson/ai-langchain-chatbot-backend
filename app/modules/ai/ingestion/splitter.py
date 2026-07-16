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
            page_number = self._resolve_page_number(doc.metadata)
            for index, text in enumerate(split_texts):
                chunk = Chunk(
                    content=text,
                    chunk_index=index,
                    page_number=page_number,
                    metadata=doc.metadata
                )
                chunks.append(chunk)
        return chunks

    @staticmethod
    def _resolve_page_number(metadata: dict) -> int | None:
        """Resolve a 1-indexed page number from loader metadata.

        `PyPDFLoader` sets a 0-indexed "page" key; other loaders (e.g. DOCX)
        have no page concept and won't set either key.
        """
        if metadata.get("page_number") is not None:
            return metadata["page_number"]
        page = metadata.get("page")
        return page + 1 if page is not None else None