from functools import lru_cache
from pydantic import BaseModel, computed_field, model_validator

from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseModel):
    APP_NAME: str
    APP_DESCRIPTION: str
    APP_VERSION: str
    ENVIRONMENT: str
    DEBUG: bool
    API_V1_PREFIX: str

class AISettings(BaseModel):
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str
    LLM_PROVIDER: str = "anthropic"
    EMBEDDING_PROVIDER: str
    EMBEDDING_MODEL: str
    EMBEDDING_DIMENSION: int
    CHUNKSIZE: int
    CHUNK_OVERLAP: int

class DatabaseSettings(BaseModel):
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str
    NAME: str
    # Relational CRUD backend: postgres | sqlserver | mongodb.
    # Independent from VECTOR_DB below.
    PROVIDER: str = "postgres"
    # Vector store backend used for embedding storage/similarity search: pgvector | qdrant | pinecone.
    # Independent from PROVIDER above (e.g. Postgres relational DB + Qdrant vectors is valid).
    VECTOR_DB: str

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            "postgresql+psycopg://"
            f"{self.USER}:"
            f"{self.PASSWORD}@"
            f"{self.HOST}:"
            f"{self.PORT}/"
            f"{self.NAME}"
        )

class StorageSettings(BaseModel):
    PROVIDER: str
    LOCAL_UPLOAD_PATH: str

class Settings(BaseSettings):
    app: AppSettings
    ai: AISettings
    database: DatabaseSettings
    storage: StorageSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def _validate_vector_db_provider_combo(self) -> "Settings":
        vector_db = self.database.VECTOR_DB.lower()
        provider = self.database.PROVIDER.lower()
        if vector_db == "pgvector" and provider != "postgres":
            raise ValueError(
                "Invalid configuration: database.VECTOR_DB='pgvector' requires "
                "database.PROVIDER='postgres' (pgvector stores vectors in the "
                f"same Postgres database). Got database.PROVIDER='{self.database.PROVIDER}'."
            )
        return self

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()