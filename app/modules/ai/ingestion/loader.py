from abc import ABC, abstractmethod 

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

class DocumentLoader(ABC):
    """Base class for document loaders."""

    @abstractmethod
    async def load(self, file_path: str) -> list[Document]:
        """Return a list of `Document` objects from the given path."""
        pass

class PDFLoader(DocumentLoader):
    """Load PDF files into `Document` objects."""

    async def load(self, file_path: str) -> list[Document]:
        """Load documents from a PDF file."""
        loader = PyPDFLoader(file_path)
        return await loader.load()