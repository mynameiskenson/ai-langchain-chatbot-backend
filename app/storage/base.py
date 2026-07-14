from abc import ABC, abstractmethod
from pathlib import Path

from fastapi import UploadFile

class StorageProvider(ABC):

    @abstractmethod
    async def save(self, file: UploadFile, filename: str) -> Path:
        """Save a file and return its storage path."""
        pass

    @abstractmethod
    async def delete(self, path: Path | str) -> None:
        """Delete a file at the given path."""
        pass

    @abstractmethod
    async def exists(self, path: Path | str) -> bool:
        """Return True if a file exists at the given path."""
        pass