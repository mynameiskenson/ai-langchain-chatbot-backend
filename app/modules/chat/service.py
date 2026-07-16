from app.modules.ai.rag.service import RAGService
from app.modules.ai.retrieval.service import RetrievalService
from app.modules.ai.prompt.service import PromptService
from app.modules.ai.providers.llm.factory import LLMFactory
from app.modules.ai.constant import AIProviderType

from app.core.dependencies import get_uow

from app.core.config import settings


class ChatService:
    """High-level chat service that uses RAG to answer queries."""

    def __init__(self):
        # Create components using sensible defaults from config/constants.
        # Embedding provider: try OLLAMA (can be adjusted later).
        self.retrieval_service = RetrievalService(uow_factory=get_uow, provider_name=AIProviderType.OLLAMA.value)
        self.prompt_service = PromptService()

        # LLM provider: default to Anthropic (changeable via factory)
        self.llm_provider = LLMFactory.create(AIProviderType.ANTHROPIC.value)

        self.rag_service = RAGService(
            retrieval_service=self.retrieval_service,
            prompt_service=self.prompt_service,
            llm_provider=self.llm_provider,
        )

    async def ask(self, query: str, top_k: int = 5, user_id: str | None = None):
        """Run a RAG-backed query and return the RAGResponse DTO."""
        from app.modules.ai.rag.dto import RAGRequest

        request = RAGRequest(query=query, user_id=user_id, top_k=top_k)
        return await self.rag_service.ask(request)
