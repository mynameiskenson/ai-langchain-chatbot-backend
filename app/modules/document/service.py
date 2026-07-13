from pathlib import Path
from typing import Callable
from uuid import uuid4

from fastapi import UploadFile

from app.uow.base import UnitOfWork
from app.storage.base import StorageProvider
from app.core.config import settings
from app.core.exceptions import NotFoundException, ValidationException

from app.modules.document.models import Document, DocumentStatus


class DocumentService:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        storage: StorageProvider,
    ):
        self.uow_factory = uow_factory
        self.storage = storage

    # ------------------------------------------------------------------
    # Upload workflow
    # ------------------------------------------------------------------

    async def upload_document(self, file: UploadFile, owner_id: str) -> Document:
        """Persist the file and record its metadata. Returns a Document in
        UPLOADED status, ready to be picked up by the ingestion pipeline."""
        if not owner_id or owner_id.strip() == "":
            raise ValidationException("Owner ID cannot be empty.")

        suffix = Path(file.filename).suffix
        stored_filename = f"{uuid4()}{suffix}"

        storage_path_obj = await self.storage.save(file, stored_filename)
        storage_path = str(storage_path_obj)

        async with self.uow_factory() as uow:
            doc = Document(
                original_filename=file.filename,
                stored_filename=stored_filename,
                mime_type=file.content_type,
                file_size=file.size,
                storage_provider=settings.storage.PROVIDER,
                storage_path=storage_path,
                owner_id=owner_id,
                status=DocumentStatus.UPLOADED,
            )
            return await uow.documents.create(doc)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    async def get_document(self, document_id: str) -> Document:
        async with self.uow_factory() as uow:
            entity = await uow.documents.get(document_id)
            if entity is None:
                raise NotFoundException(f"Document '{document_id}' not found.")
            return entity

    async def list_documents(self, owner_id: str) -> list[Document]:
        async with self.uow_factory() as uow:
            result = await uow.documents.get_document_by_owner(owner_id)
            if not result:
                raise NotFoundException(f"No documents found for owner '{owner_id}'.")
            return result

    # ------------------------------------------------------------------
    # Lifecycle transitions
    # ------------------------------------------------------------------

    async def mark_processing(self, document_id: str) -> Document:
        async with self.uow_factory() as uow:
            entity = await uow.documents.get(document_id)
            if entity is None:
                raise NotFoundException(f"Document '{document_id}' not found.")
            return await uow.documents.update(entity, {"status": DocumentStatus.PROCESSING})

    async def mark_ready(self, document_id: str) -> Document:
        async with self.uow_factory() as uow:
            entity = await uow.documents.get(document_id)
            if entity is None:
                raise NotFoundException(f"Document '{document_id}' not found.")
            return await uow.documents.update(entity, {"status": DocumentStatus.READY})

    async def mark_failed(self, document_id: str) -> Document:
        async with self.uow_factory() as uow:
            entity = await uow.documents.get(document_id)
            if entity is None:
                raise NotFoundException(f"Document '{document_id}' not found.")
            return await uow.documents.update(entity, {"status": DocumentStatus.FAILED})