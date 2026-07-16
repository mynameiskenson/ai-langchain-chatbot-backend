from fastapi import APIRouter

from app.core.utils import sanitize_metadata

from app.schemas.response import ApiResponse

from app.modules.chat.service import ChatService
from app.modules.chat.schemas import ChatRequestSchema, ChatResultSchema


chat_router = APIRouter()
service = ChatService()


@chat_router.post(
    "/chat",
    response_model=ApiResponse[ChatResultSchema],
    summary="Ask (RAG)",
    description="Ask a question using Retrieval-Augmented Generation (RAG).",
)
async def ask_chat(request: ChatRequestSchema):
    result = await service.ask(query=request.query, top_k=request.top_k, user_id=request.user_id)

    serialized_chunks = []
    for rc in result.retrieved_chunks:
        metadata = sanitize_metadata(rc.metadata)
        serialized_chunks.append({
            "document_id": str(rc.document_id),
            "content": rc.content,
            "chunk_index": rc.chunk_index,
            "page_number": rc.page_number,
            "metadata": metadata,
            "score": float(getattr(rc, "score", None)) if getattr(rc, "score", None) is not None else None,
        })

    chat_result = {
        "response": result.response,
        "retrieved_chunks": serialized_chunks,
    }

    return ApiResponse(data=ChatResultSchema.model_validate(chat_result))
