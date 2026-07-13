from functools import lru_cache
from pydantic import BaseModel, computed_field

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

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()