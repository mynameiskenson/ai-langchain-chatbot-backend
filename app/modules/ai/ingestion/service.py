from app.core.utils import sha256
from typing import Callable
from typing import Optional

from app.uow.base import UnitOfWork

from app.modules.ai.ingestion.loader import DocumentLoader
from app.modules.ai.ingestion.splitter import TextSplitter
from app.modules.ai.ingestion.dto import Chunk
from uuid import UUID

from app.modules.document.models import DocumentChunk, DocumentStatus

from app.modules.ai.providers.embeddings.base import EmbeddingProvider
from app.modules.ai.providers.embeddings.dto import Embedding as EmbeddingDTO

from app.modules.ai.providers.vectorstore.base import VectorStoreProvider
from app.modules.ai.providers.vectorstore.dto import VectorRecord


class IngestionService:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        loader: DocumentLoader,
        splitter: TextSplitter,
        vector_store: VectorStoreProvider,
        embedding_provider: EmbeddingProvider,
        document_service: Optional[object] = None,
    ):
        """Create an ingestion service.

        `embedding_provider` and `vector_store` must be fully constructed
        provider instances (built via their respective factories, e.g.
        `app.core.dependencies.get_embedding_provider`/`get_vector_store`) -
        this service does not select/construct providers itself.
        """
        self.uow_factory = uow_factory
        self.loader = loader
        self.splitter = splitter
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        # Optional higher-level DocumentService for lifecycle updates
        self.document_service = document_service

    async def process_documents(self, file_path: str, document_id: UUID) -> list[Chunk]:
        """Load a file, split it into chunks, compute embeddings, and save them.

        This method marks the `Document` as PROCESSING at the start, marks it
        READY on success, and marks it FAILED if an exception occurs.
        """
        # mark processing (use DocumentService if provided)
        if self.document_service is not None:
            try:
                await self.document_service.mark_processing(str(document_id))
            except Exception:
                # fall back to direct uow update if service fails
                async with self.uow_factory() as uow:
                    doc = await uow.documents.get(document_id)
                    if doc:
                        await uow.documents.update(doc, {"status": DocumentStatus.PROCESSING})
        else:
            async with self.uow_factory() as uow:
                doc = await uow.documents.get(document_id)
                if doc:
                    await uow.documents.update(doc, {"status": DocumentStatus.PROCESSING})

        try:
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

            # Persist the chunk rows (content/metadata) to the relational database.
            # Embeddings are NOT stored here; they are delegated to the vector store.
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
                    )
                )

            async with self.uow_factory() as uow:
                created = await uow.document_chunks.create_many(entities)

            # Upsert embeddings (+ duplicated content/metadata) into the vector store
            if self.embedding_provider and created:
                records = [
                    VectorRecord(
                        chunk_id=entity.id,
                        document_id=document_id,
                        embedding=chunk.embedding.vector,
                        content=chunk.content,
                        chunk_index=chunk.chunk_index,
                        page_number=chunk.page_number,
                        metadata=chunk.metadata,
                    )
                    for entity, chunk in zip(created, chunks)
                    if chunk.embedding is not None
                ]
                if records:
                    await self.vector_store.upsert(records)

            # mark ready via DocumentService when present, else uow
            if self.document_service is not None:
                await self.document_service.mark_ready(str(document_id))
            else:
                async with self.uow_factory() as uow:
                    await uow.documents.update(await uow.documents.get(document_id), {"status": DocumentStatus.READY})

            return chunks

        except Exception:
            # mark document failed on any exception
            # mark failed via DocumentService when present, else uow
            if self.document_service is not None:
                await self.document_service.mark_failed(str(document_id))
            else:
                async with self.uow_factory() as uow:
                    maybe_doc = await uow.documents.get(document_id)
                    if maybe_doc:
                        await uow.documents.update(maybe_doc, {"status": DocumentStatus.FAILED})
            raise