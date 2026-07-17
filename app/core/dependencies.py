from app.core.config import settings
from functools import lru_cache
from fastapi import Depends

# ======================================================
# Health service dependency
# ======================================================
from app.modules.health.service import HealthService

def get_health_service() -> HealthService:
    return HealthService()

# ======================================================
# Database session dependency
# ======================================================
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from app.database.session import AsyncSessionLocal
from app.uow.sqlalchemy import SQLAlchemyUnitOfWork


def get_db() -> None:
    # kept for compatibility if sync db used elsewhere
    raise RuntimeError("use async sessions via get_uow")


@asynccontextmanager
async def get_uow() -> AsyncGenerator[SQLAlchemyUnitOfWork, None]:
    async with AsyncSessionLocal() as session:
        async with SQLAlchemyUnitOfWork(session) as uow:
            yield uow

# ======================================================
# Vector store provider dependency
# ======================================================
from app.modules.ai.providers.vectorstore.base import VectorStoreProvider
from app.modules.ai.providers.vectorstore.factory import VectorStoreFactory


def get_vector_store() -> VectorStoreProvider:
    """Return a configured VectorStoreProvider instance based on settings.

    Independent from the relational DB provider (`settings.database.PROVIDER`);
    this only controls where embeddings are stored/searched.
    """
    return VectorStoreFactory.create(settings.database.VECTOR_DB, uow_factory=get_uow)

# ======================================================
# Storage provider dependency
# ======================================================
from app.storage.factory import get_storage
from app.storage.local import LocalStorage


def get_storage_provider() -> LocalStorage:
    """Return a configured LocalStorage instance based on settings."""
    return get_storage()
