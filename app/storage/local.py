import shutil
from pathlib import Path

from fastapi import UploadFile

from app.storage.base import StorageProvider

class LocalStorage(StorageProvider):
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, file: UploadFile, filename: str) -> Path:
        file_path = self.base_path / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file_path

    async def delete(self, path: Path | str) -> None:
        p = Path(path)
        file_path = self.base_path / p
        if file_path.exists():
            file_path.unlink()

    async def exists(self, path: Path | str) -> bool:
        p = Path(path)
        file_path = self.base_path / p
        return file_path.exists()