from app.core.utils import sha256
from typing import Callable

from app.uow.base import UnitOfWork

from app.modules.ai.ingestion.loader import DocumentLoader
from app.modules.ai.ingestion.splitter import TextSplitter
from app.modules.ai.ingestion.dto import Chunk
from uuid import UUID

from app.modules.document.models import DocumentChunk, DocumentStatus

from app.modules.ai.providers.embeddings.factory import EmbeddingFactory
from app.modules.ai.providers.embeddings.base import EmbeddingProvider
from app.modules.ai.providers.embeddings.dto import Embedding as EmbeddingDTO


class IngestionService:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        loader: DocumentLoader,
        splitter: TextSplitter,
        embedding_provider: EmbeddingProvider | None = None,
        provider_name: str | None = None,
    ):
        """Create an ingestion service.

        Pass either an `embedding_provider` instance or a `provider_name` string.
        """
        self.uow_factory = uow_factory
        self.loader = loader
        self.splitter = splitter

        if provider_name is not None:
            self.embedding_provider = EmbeddingFactory.create(provider_name)
        else:
            self.embedding_provider = embedding_provider

    async def process_documents(self, file_path: str, document_id: UUID) -> list[Chunk]:
        """Load a file, split it into chunks, compute embeddings, and save them."""
        documents = await self.loader.load(file_path)
        chunks = await self.splitter.split(documents)

        # Compute embeddings for each chunk if an embedding provider is available
        if self.embedding_provider and chunks:
            texts = [c.content for c in chunks]
            vectors = await self.embedding_provider.embed_documents(texts)

            model = getattr(self.embedding_provider, "model", "")
            dimension = getattr(self.embedding_provider, "dimension", 0)

            for chunk, vec in zip(chunks, vectors):
                chunk.embedding = EmbeddingDTO(vector=vec, model=model, dimension=dimension)
        
        # Persist the chunks to the database
        entities = []
        for chunk in chunks:
            entities.append(
                DocumentChunk(
                    document_id=document_id,
                    content_hash=sha256(chunk.content),
                    content=chunk.content,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    chunk_metadata=chunk.metadata,
                    embedding=(chunk.embedding.vector if chunk.embedding else None),
                )
            )

        # Update the document status to READY after successfully creating the chunks
        async with self.uow_factory() as uow:
            await uow.document_chunks.create_many(entities)
            await uow.documents.update(await uow.documents.get(document_id), status=DocumentStatus.READY)

        return chunks