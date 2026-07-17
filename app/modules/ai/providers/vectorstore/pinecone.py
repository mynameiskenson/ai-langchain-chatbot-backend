from uuid import UUID

from app.modules.ai.providers.vectorstore.base import VectorStoreProvider
from app.modules.ai.providers.vectorstore.dto import VectorRecord, VectorSearchResult


class PineconeVectorStore(VectorStoreProvider):
    """Scaffolded Pinecone provider. Not implemented yet.

    Intended shape once implemented: an index named after the project (sized
    to `settings.ai.EMBEDDING_DIMENSION`), vectors keyed by
    `VectorRecord.chunk_id` (stringified), metadata containing
    content/document_id/chunk_index/page_number for filtering.
    """

    def __init__(self, api_key: str | None = None, environment: str | None = None, index_name: str | None = None):
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name or "document-chunks"

    async def upsert(self, records: list[VectorRecord]) -> None:
        raise NotImplementedError("Pinecone vector store support is not implemented yet.")

    async def search(self, query_embedding: list[float], top_k: int = 5, filters: dict | None = None) -> list[VectorSearchResult]:
        raise NotImplementedError("Pinecone vector store support is not implemented yet.")

    async def delete_by_document(self, document_id: UUID) -> None:
        raise NotImplementedError("Pinecone vector store support is not implemented yet.")
