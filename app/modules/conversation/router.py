from fastapi import APIRouter

from app.schemas.response import ApiResponse
from app.core.dependencies import get_uow
from app.modules.conversation.service import ConversationService
from app.modules.conversation.schemas import ConversationCreateSchema, ConversationResponseSchema

conversation_router = APIRouter()
service = ConversationService(uow_factory=get_uow)

@conversation_router.post(
        "/conversations", 
        response_model=ApiResponse[ConversationResponseSchema], 
        summary="Create Conversation", 
        description="Create a new conversation."
    )
async def create_conversation(conversation: ConversationCreateSchema):
    result = await service.create_conversation(title=conversation.title, owner_id=conversation.owner_id)
    return ApiResponse(data=ConversationResponseSchema.model_validate(result))

@conversation_router.get(
        "/conversations/{conversation_id}", 
        response_model=ApiResponse[ConversationResponseSchema], 
        summary="Get Conversation", 
        description="Retrieve a conversation by its ID."
    )
async def get_conversation(conversation_id: str):
    result = await service.get_conversation(conversation_id)
    return ApiResponse(data=ConversationResponseSchema.model_validate(result))

@conversation_router.get(
        "/conversations/owner/{owner_id}", 
        response_model=ApiResponse[list[ConversationResponseSchema]], 
        summary="Get Conversations by Owner", 
        description="Retrieve all conversations for a specific owner."
    )
async def get_conversations_by_owner(owner_id: str):
    result = await service.get_conversations_by_owner(owner_id)
    return ApiResponse(data=[ConversationResponseSchema.model_validate(convo) for convo in result])

@conversation_router.put(
        "/conversations/{conversation_id}", 
        response_model=ApiResponse[ConversationResponseSchema], 
        summary="Update Conversation", 
        description="Update an existing conversation."
    )
async def archive_conversation(conversation_id: str):
    result = await service.archive_conversation(conversation_id)
    return ApiResponse(data=ConversationResponseSchema.model_validate(result))