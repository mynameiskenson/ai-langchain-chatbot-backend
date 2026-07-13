import pytest

from app.modules.document.models import DocumentChunk, Document
from app.core.config import settings


@pytest.mark.asyncio
async def test_document_chunk_repository(test_uow):
    # Use the Unit of Work so repositories share the same session
    async with test_uow as uow:
        # Create a parent document so the chunk can reference a UUID
        doc = Document(
            owner_id="test-owner",
            original_filename="test.pdf",
            stored_filename="test-stored.pdf",
            mime_type="application/pdf",
            file_size=123,
            storage_provider="local",
            storage_path="/tmp/test-stored.pdf",
        )
        saved_doc = await uow.documents.create(doc)

        # Create an embedding placeholder with the configured dimension
        dim = settings.ai.EMBEDDING_DIMENSION
        embedding = [0.0] * dim

        chunk = DocumentChunk(
            document_id=saved_doc.id,
            chunk_index=0,
            content="This is a test chunk.",
            chunk_metadata={"source": "test"},
            content_hash="testhash",
            embedding=embedding,
            page_number=1,
        )

        # Save the chunk to the database
        saved_chunk = await uow.document_chunks.create(chunk)

        assert saved_chunk.id is not None, "Chunk ID should be set after creation"
        assert saved_chunk.document_id == saved_doc.id, "Chunk should be associated with the correct document ID"
        assert saved_chunk.content == "This is a test chunk.", "Chunk content should match the input"