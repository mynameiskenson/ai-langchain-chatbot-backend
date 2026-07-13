from app.modules.ai.ingestion.loader import DocumentLoader
from app.modules.ai.ingestion.splitter import TextSplitter
from app.modules.ai.ingestion.dto import Chunk

class IngestionService:
    def __init__(self, loader: DocumentLoader, splitter: TextSplitter):
        self.loader = loader
        self.splitter = splitter

    def create_chunks(self, file_path: str) -> list[Chunk]:
        """Load a document from a file and split it into chunks."""
        documents = self.loader.load(file_path)
        chunks = self.splitter.split(documents)
        return chunks