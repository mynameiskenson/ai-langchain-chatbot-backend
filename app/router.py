from fastapi import APIRouter

from app.modules.health.router import health_router
from app.modules.system.router import error_router
from app.modules.conversation.router import conversation_router
from app.modules.document.router import document_router
from app.modules.chat.router import chat_router

from app.core.config import settings

api_router = APIRouter()

api_router.include_router(health_router, prefix=settings.app.API_V1_PREFIX, tags=["Health"])
api_router.include_router(error_router, prefix=settings.app.API_V1_PREFIX, tags=["Error"])
api_router.include_router(conversation_router, prefix=settings.app.API_V1_PREFIX, tags=["Conversation"])
api_router.include_router(document_router, prefix=settings.app.API_V1_PREFIX, tags=["Document"])
api_router.include_router(chat_router, prefix=settings.app.API_V1_PREFIX, tags=["Chat"])