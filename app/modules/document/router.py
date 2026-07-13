from fastapi import APIRouter, UploadFile, Depends
from app.schemas.response import ApiResponse
from app.core.dependencies import get_storage_provider, get_uow
from app.storage.validators import validate_upload
from app.modules.document.service import DocumentService
from app.modules.document.schemas import DocumentResponseSchema

document_router = APIRouter()
service = DocumentService(uow_factory=get_uow, storage=get_storage_provider())

@document_router.post(
        "/documents", 
        response_model=ApiResponse[DocumentResponseSchema], 
        summary="Upload Document", 
        description="Upload a new document."
    )
async def upload_document(file: UploadFile = Depends(validate_upload), owner_id: str = None):
    result = await service.upload_document(file=file, owner_id=owner_id)
    return ApiResponse(data=DocumentResponseSchema.model_validate(result))

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
        "/documents/owner/{owner_id}", 
        response_model=ApiResponse[list[DocumentResponseSchema]], 
        summary="Get Documents by Owner", 
        description="Retrieve all documents for a specific owner."
    )
async def get_documents_by_owner(owner_id: str):
    result = await service.list_documents(owner_id)
    return ApiResponse(data=[DocumentResponseSchema.model_validate(doc) for doc in result])