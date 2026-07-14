from app.modules.ai.rag.dto import RAGRequest, RAGResponse
from app.modules.ai.prompt.dto import PromptRequest

from app.modules.ai.retrieval.service import RetrievalService
from app.modules.ai.prompt.service import PromptService
from app.modules.ai.providers.llm.base import LLMProvider
from app.modules.ai.providers.llm.factory import LLMFactory

class RAGService:
    def __init__(self, retrieval_service: RetrievalService, prompt_service: PromptService, llm_provider: LLMProvider, provider_name: str | None = None):
        self.retrieval_service = retrieval_service
        self.prompt_service = prompt_service

        if provider_name is not None:
            self.llm_provider = LLMFactory.create(provider_name)
        else:
            self.llm_provider = llm_provider

    async def ask(self, request: RAGRequest) -> RAGResponse:
        # Step 1: Retrieve relevant chunks based on the query
        # RetrievalService exposes `semantic_search`; use that to get top_k chunks.
        retrieved_chunks = await self.retrieval_service.semantic_search(request.query, top_k=request.top_k)

        # Step 2: Build the prompt request with the retrieved context
        context = "\n\n".join(chunk.content for chunk in retrieved_chunks)
        prompt_request = PromptRequest(
            question=request.query,
            context=context,
            history=[]  # Assuming no history for simplicity; can be extended as needed
        )

        # Step 3: Build chat messages using the PromptService
        messages = self.prompt_service.build_messages(prompt_request)

        # Step 4: Send the messages to the LLM provider and get a response
        chat_response = await self.llm_provider.chat(messages)

        # Step 5: Return the RAGResponse containing the chat response and retrieved chunks
        return RAGResponse(response=chat_response, retrieved_chunks=retrieved_chunks)