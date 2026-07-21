import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

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
    conversation_id = str(request.conversation_id) if request.conversation_id else None
    result, conversation_id = await service.ask(query=request.query, top_k=request.top_k, user_id=request.user_id, conversation_id=conversation_id)

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
        "conversation_id": conversation_id,
    }

    return ApiResponse(data=ChatResultSchema.model_validate(chat_result))

@chat_router.post(
    "/chat/stream",
    summary="Ask (RAG) with streaming",
    description="Ask a question using Retrieval-Augmented Generation (RAG) with streaming response.",
)
async def stream_ask_chat(request: ChatRequestSchema):
    conversation_id = str(request.conversation_id) if request.conversation_id else None

    async def event_generator():
        async for chunk, conv_id in service.stream_ask(
            query=request.query,
            top_k=request.top_k,
            user_id=request.user_id,
            conversation_id=conversation_id,
        ):
            payload = {
                "content": chunk.content,
                "is_final": chunk.is_final,
                "model": chunk.model,
                "finish_reason": chunk.finish_reason,
                "conversation_id": conv_id,
            }
            yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
