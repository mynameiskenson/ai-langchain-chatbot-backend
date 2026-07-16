from abc import ABC, abstractmethod
import asyncio
from pathlib import Path
from typing import List

from langchain_core.documents import Document

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader


class DocumentLoader(ABC):
    """Base class for document loaders."""

    @abstractmethod
    async def load(self, file_path: str) -> List[Document]:
        """Return a list of `Document` objects from the given path."""


class PDFLoader(DocumentLoader):
    """Load PDF files into `Document` objects."""

    async def load(self, file_path: str) -> List[Document]:
        loader = PyPDFLoader(file_path)
        # many langchain loaders are synchronous; run in a thread to avoid blocking
        docs = await asyncio.to_thread(loader.load)
        return docs


class DocxLoader(DocumentLoader):
    """Load DOCX files into `Document` objects.

    This uses `Docx2txtLoader` from `langchain_community` when available.
    If it's not installed, an informative error is raised.
    """

    async def load(self, file_path: str) -> List[Document]:
        if Docx2txtLoader is None:
            raise RuntimeError(
                "No DOCX loader available. Install a loader (e.g. upgrade langchain-community) or add a DOCX parser."
            )
        loader = Docx2txtLoader(file_path)
        docs = await asyncio.to_thread(loader.load)
        return docs


class AutoLoader(DocumentLoader):
    """Auto-selects a loader based on file extension (supports .pdf and .docx)."""

    def __init__(self):
        self._pdf = PDFLoader()
        self._docx = DocxLoader()

    async def load(self, file_path: str) -> List[Document]:
        suffix = Path(file_path).suffix.lower()
        if suffix == ".pdf":
            return await self._pdf.load(file_path)
        if suffix == ".docx":
            return await self._docx.load(file_path)
        raise ValueError(f"Unsupported file type: {suffix}. Supported: .pdf, .docx")