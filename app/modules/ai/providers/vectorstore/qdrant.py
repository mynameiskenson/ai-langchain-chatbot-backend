from uuid import UUID

from app.modules.ai.providers.vectorstore.base import VectorStoreProvider
from app.modules.ai.providers.vectorstore.dto import VectorRecord, VectorSearchResult


class QdrantVectorStore(VectorStoreProvider):
    """Scaffolded Qdrant provider. Not implemented yet.

    Intended shape once implemented: a collection named after the project
    (sized to `settings.ai.EMBEDDING_DIMENSION`), points keyed by
    `VectorRecord.chunk_id`, payload containing content/metadata/document_id
    for filtering.
    """

    def __init__(self, url: str | None = None, api_key: str | None = None, collection_name: str | None = None):
        self.url = url
        self.api_key = api_key
        self.collection_name = collection_name or "document_chunks"

    async def upsert(self, records: list[VectorRecord]) -> None:
        raise NotImplementedError("Qdrant vector store support is not implemented yet.")

    async def search(self, query_embedding: list[float], top_k: int = 5, filters: dict | None = None) -> list[VectorSearchResult]:
        raise NotImplementedError("Qdrant vector store support is not implemented yet.")

    async def delete_by_document(self, document_id: UUID) -> None:
        raise NotImplementedError("Qdrant vector store support is not implemented yet.")
