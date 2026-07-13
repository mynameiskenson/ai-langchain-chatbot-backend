from abc import ABC, abstractmethod 

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

class DocumentLoader(ABC):
    """Abstract base class for document loaders."""

    @abstractmethod
    async def load(self, file_path: str) -> list[Document]:
        """Load documents from a source."""
        pass

class PDFLoader(DocumentLoader):
    """Concrete implementation of DocumentLoader for PDF files."""

    async def load(self, file_path: str) -> list[Document]:
        """Load documents from a PDF file."""
        loader = PyPDFLoader(file_path)
        return await loader.load()