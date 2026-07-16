from fastapi import APIRouter, UploadFile, BackgroundTasks, File

from app.schemas.response import ApiResponse
from app.core.dependencies import get_storage_provider, get_uow
from app.storage.validators import validate_upload
from app.modules.document.service import DocumentService
from app.modules.document.schemas import DocumentResponseSchema
from app.modules.ai.ingestion.loader import AutoLoader
from app.modules.ai.ingestion.splitter import RecursiveTextSplitter
from app.modules.ai.ingestion.service import IngestionService
from app.core.config import settings

document_router = APIRouter()
service = DocumentService(uow_factory=get_uow, storage=get_storage_provider())

# Ingestion service used to process uploaded documents in background
ingestion = IngestionService(
    uow_factory=get_uow,
    loader=AutoLoader(),
    splitter=RecursiveTextSplitter(),
    provider_name=settings.ai.EMBEDDING_PROVIDER,
    document_service=service,
)

@document_router.post(
        "/documents",
        response_model=ApiResponse[list[DocumentResponseSchema]],
        summary="Upload Documents",
        description="Upload one or more documents."
    )
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    user_id: str = None,
):
    """Accept multiple uploaded files, store them, and enqueue ingestion in background.

    All-or-nothing: every file is validated before any file is saved, so an
    invalid file rejects the whole batch without persisting anything. If a
    file fails to save/process after some files in the batch were already
    saved, those already-saved documents are rolled back (storage + DB).
    """
    # Validate every file up front; a single invalid file fails the whole batch.
    for f in files:
        await validate_upload(f)

    results = []
    try:
        for f in files:
            doc = await service.upload_document(file=f, user_id=user_id)
            results.append(doc)
            background_tasks.add_task(ingestion.process_documents, doc.storage_path, doc.id)
    except Exception:
        # Roll back any documents already saved in this batch
        for doc in results:
            await service.delete_document(doc.id)
        raise

    return ApiResponse(data=[DocumentResponseSchema.model_validate(d) for d in results])

@document_router.get(
        "/documents/{document_id}", 
        response_model=ApiResponse[DocumentResponseSchema], 
        summary="Get Document", 
        description="Retrieve a document by its ID."
    )
async def get_document(document_id: str):
    result = await service.get_document(document_id)
    return ApiResponse(data=DocumentResponseSchema.model_validate(result))

@document_router.get(
        "/documents/user/{user_id}", 
        response_model=ApiResponse[list[DocumentResponseSchema]], 
        summary="Get Documents by User", 
        description="Retrieve all documents for a specific user."
    )
async def get_documents_by_user(user_id: str):
    result = await service.list_documents(user_id)
    return ApiResponse(data=[DocumentResponseSchema.model_validate(doc) for doc in result])