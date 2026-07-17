import pytest

from app.modules.ai.providers.vectorstore.factory import VectorStoreFactory
from app.modules.ai.providers.vectorstore.pgvector import PgVectorStore
from app.modules.ai.providers.vectorstore.qdrant import QdrantVectorStore
from app.modules.ai.providers.vectorstore.pinecone import PineconeVectorStore


def _dummy_uow_factory():
    raise AssertionError("uow_factory should not be called during construction")


def test_factory_returns_pgvector_store():
    store = VectorStoreFactory.create("pgvector", uow_factory=_dummy_uow_factory)
    assert isinstance(store, PgVectorStore)


def test_factory_returns_qdrant_stub():
    store = VectorStoreFactory.create("qdrant", uow_factory=_dummy_uow_factory)
    assert isinstance(store, QdrantVectorStore)


def test_factory_returns_pinecone_stub():
    store = VectorStoreFactory.create("pinecone", uow_factory=_dummy_uow_factory)
    assert isinstance(store, PineconeVectorStore)


def test_factory_rejects_unknown_provider():
    with pytest.raises(ValueError):
        VectorStoreFactory.create("unknown", uow_factory=_dummy_uow_factory)


@pytest.mark.asyncio
async def test_qdrant_stub_raises_not_implemented():
    store = QdrantVectorStore()
    with pytest.raises(NotImplementedError):
        await store.upsert([])
    with pytest.raises(NotImplementedError):
        await store.search([0.0])
    with pytest.raises(NotImplementedError):
        await store.delete_by_document("00000000-0000-0000-0000-000000000000")


@pytest.mark.asyncio
async def test_pinecone_stub_raises_not_implemented():
    store = PineconeVectorStore()
    with pytest.raises(NotImplementedError):
        await store.upsert([])
    with pytest.raises(NotImplementedError):
        await store.search([0.0])
    with pytest.raises(NotImplementedError):
        await store.delete_by_document("00000000-0000-0000-0000-000000000000")
