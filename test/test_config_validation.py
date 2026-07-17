import pytest
from pydantic import ValidationError

from app.core.config import Settings, AppSettings, AISettings, DatabaseSettings, StorageSettings


def _base_kwargs(vector_db: str, provider: str) -> dict:
    return dict(
        app=AppSettings(
            APP_NAME="test",
            APP_DESCRIPTION="test",
            APP_VERSION="0.0.0",
            ENVIRONMENT="test",
            DEBUG=True,
            API_V1_PREFIX="/api/v1",
        ),
        ai=AISettings(
            ANTHROPIC_API_KEY="key",
            ANTHROPIC_MODEL="model",
            EMBEDDING_PROVIDER="ollama",
            EMBEDDING_MODEL="embed-model",
            EMBEDDING_DIMENSION=768,
            CHUNKSIZE=1000,
            CHUNK_OVERLAP=200,
        ),
        database=DatabaseSettings(
            HOST="localhost",
            PORT=5432,
            USER="postgres",
            PASSWORD="pw",
            NAME="db",
            PROVIDER=provider,
            VECTOR_DB=vector_db,
        ),
        storage=StorageSettings(PROVIDER="local", LOCAL_UPLOAD_PATH="upload"),
    )


def test_pgvector_with_postgres_is_valid():
    settings = Settings(**_base_kwargs("pgvector", "postgres"))
    assert settings.database.VECTOR_DB == "pgvector"
    assert settings.database.PROVIDER == "postgres"


def test_pgvector_with_mongodb_is_rejected():
    with pytest.raises(ValidationError):
        Settings(**_base_kwargs("pgvector", "mongodb"))


def test_pgvector_with_sqlserver_is_rejected():
    with pytest.raises(ValidationError):
        Settings(**_base_kwargs("pgvector", "sqlserver"))


def test_qdrant_with_mongodb_is_valid():
    settings = Settings(**_base_kwargs("qdrant", "mongodb"))
    assert settings.database.VECTOR_DB == "qdrant"
    assert settings.database.PROVIDER == "mongodb"


def test_pinecone_with_sqlserver_is_valid():
    settings = Settings(**_base_kwargs("pinecone", "sqlserver"))
    assert settings.database.VECTOR_DB == "pinecone"
    assert settings.database.PROVIDER == "sqlserver"
