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

    async def upload_document(self, file: UploadFile, user_id: str) -> Document:
        """Save an uploaded file and create a `Document` record (status UPLOADED)."""
        if not user_id or user_id.strip() == "":
            raise ValidationException("User ID cannot be empty.")

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
                user_id=user_id,
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

    async def list_documents(self, user_id: str) -> list[Document]:
        async with self.uow_factory() as uow:
            result = await uow.documents.get_document_by_user(user_id)
            if not result:
                raise NotFoundException(f"No documents found for user '{user_id}'.")
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

    # ------------------------------------------------------------------
    # Rollback / cleanup
    # ------------------------------------------------------------------

    async def delete_document(self, document_id: str) -> None:
        """Delete a document's stored file and its database record.

        Used to roll back a document that was saved as part of a batch
        upload when a later file in the same batch fails.
        """
        async with self.uow_factory() as uow:
            entity = await uow.documents.get(document_id)
            if entity is None:
                return
            await self.storage.delete(entity.storage_path)
            await uow.documents.delete(document_id)