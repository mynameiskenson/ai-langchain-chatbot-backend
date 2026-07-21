from app.modules.ai.rag.service import RAGService
from app.modules.ai.retrieval.service import RetrievalService
from app.modules.ai.prompt.service import PromptService
from app.modules.conversation.service import ConversationService
from app.modules.message.service import MessageService

from app.core.dependencies import get_uow, get_vector_store, get_embedding_provider, get_llm_provider

from app.modules.ai.rag.dto import RAGRequest

class ChatService:
    """High-level chat service that uses RAG to answer queries."""

    def __init__(self):
        # Providers are constructed centrally via the factories (through the
        # app.core.dependencies helpers) based on settings; this service just
        # wires the ready-made instances together.
        self.retrieval_service = RetrievalService(
            uow_factory=get_uow,
            vector_store=get_vector_store(),
            embedding_provider=get_embedding_provider(),
        )
        self.prompt_service = PromptService()
        self.rag_service = RAGService(
            retrieval_service=self.retrieval_service,
            prompt_service=self.prompt_service,
            llm_provider=get_llm_provider(),
        )
        self.conversation_service = ConversationService(uow_factory=get_uow)
        self.message_service = MessageService(uow_factory=get_uow)

    async def _resolve_conversation_id(self, uow, user_id: str | None, conversation_id: str | None, title: str | None = None) -> str:
        """Resolve the conversation ID to use for the chat session.

        If a conversation ID is provided, it is used. If not, a new conversation
        is created for the user (if user_id is provided) or an anonymous
        conversation is created.
        """
        if conversation_id:
            return str(conversation_id)

        conversation = await self.conversation_service.create_conversation(
            title=title or "New Conversation",
            user_id=user_id or "anonymous",
            uow=uow,
        )
        return str(conversation.id)

    async def ask(self, query: str, top_k: int = 5, user_id: str | None = None, conversation_id: str | None = None):
        """Run a RAG-backed query and return the RAGResponse DTO."""

        # Resolve the conversation, fetch history and record the user message
        # atomically in a single transaction (kept separate from the LLM call
        # below so the DB connection isn't held open during the request).
        async with get_uow() as uow:
            conversation_id = await self._resolve_conversation_id(uow, user_id=user_id, conversation_id=conversation_id, title=query[:255])
            history = await self.message_service.get_history(conversation_id=conversation_id, limit=10, uow=uow)
            await self.message_service.append_message(conversation_id=conversation_id, role="user", content=query, uow=uow)

        request = RAGRequest(query=query, user_id=user_id, top_k=top_k)
        result = await self.rag_service.ask(request, history=history)

        async with get_uow() as uow:
            await self.message_service.append_message(conversation_id=conversation_id, role="assistant", content=result.response.content, uow=uow)

        return result, conversation_id
    
    async def stream_ask(self, query: str, top_k: int = 5, user_id: str | None = None, conversation_id: str | None = None):
        """Run a RAG-backed query and stream the response chunks."""

        async with get_uow() as uow:
            conversation_id = await self._resolve_conversation_id(uow, user_id=user_id, conversation_id=conversation_id, title=query[:255])
            history = await self.message_service.get_history(conversation_id=conversation_id, limit=10, uow=uow)
            await self.message_service.append_message(conversation_id=conversation_id, role="user", content=query, uow=uow)

        request = RAGRequest(query=query, user_id=user_id, top_k=top_k)
        assembled = []
        rag_stream_response = await self.rag_service.ask_stream(request, history=history)
        # Stream the chat response chunks
        async for chunk in rag_stream_response.chunks:
            assembled.append(chunk.content)
            yield chunk, conversation_id

        async with get_uow() as uow:
            await self.message_service.append_message(conversation_id=conversation_id, role="assistant", content="".join(assembled), uow=uow)
