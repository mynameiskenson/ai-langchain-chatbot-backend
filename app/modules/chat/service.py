from app.modules.ai.rag.service import RAGService
from app.modules.ai.retrieval.service import RetrievalService
from app.modules.ai.prompt.service import PromptService

from app.core.dependencies import get_uow, get_vector_store, get_embedding_provider, get_llm_provider


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

    async def ask(self, query: str, top_k: int = 5, user_id: str | None = None):
        """Run a RAG-backed query and return the RAGResponse DTO."""
        from app.modules.ai.rag.dto import RAGRequest

        request = RAGRequest(query=query, user_id=user_id, top_k=top_k)
        return await self.rag_service.ask(request)
