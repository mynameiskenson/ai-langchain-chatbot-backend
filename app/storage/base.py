from abc import ABC, abstractmethod
from pathlib import Path

from fastapi import UploadFile

class StorageProvider(ABC):

    @abstractmethod
    async def save(self, file: UploadFile, filename: str) -> Path:
        """
        Save the file to the storage provider and return the Path
        where it was saved.
        """
        pass

    @abstractmethod
    async def delete(self, path: Path | str) -> None:
        """Delete the file at the given path (or path string) from the storage provider."""
        pass

    @abstractmethod
    async def exists(self, path: Path | str) -> bool:
        """Check if a file exists at the given path (or path string) in the storage provider."""
        pass