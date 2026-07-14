from fastapi import APIRouter

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
    result = await service.ask(query=request.query, top_k=request.top_k, owner_id=request.owner_id)
    return ApiResponse(data=ChatResultSchema.model_validate(result))
