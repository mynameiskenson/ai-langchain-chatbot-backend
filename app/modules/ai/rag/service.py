from app.modules.ai.rag.dto import RAGRequest, RAGResponse, RAGStreamResponse
from app.modules.ai.prompt.dto import PromptRequest
from app.modules.ai.providers.llm.dto import ChatMessage, ChatResponse, ChatStreamChunk

from app.modules.ai.retrieval.service import RetrievalService
from app.modules.ai.prompt.service import PromptService
from app.modules.ai.providers.llm.base import LLMProvider

class RAGService:
    def __init__(self, retrieval_service: RetrievalService, prompt_service: PromptService, llm_provider: LLMProvider):
        """`llm_provider` must be a fully constructed provider instance (built via
        `app.modules.ai.providers.llm.factory.LLMFactory`, e.g. through
        `app.core.dependencies.get_llm_provider`) - this service does not
        select/construct providers itself.
        """
        self.retrieval_service = retrieval_service
        self.prompt_service = prompt_service
        self.llm_provider = llm_provider

    async def _build_messages(self, request: RAGRequest, history: list[ChatMessage]):
        if history is None:
            history = []

        # Step 1: Retrieve relevant chunks based on the query
        retrieved_chunks = await self.retrieval_service.semantic_search(request.query, top_k=request.top_k)

        # Step 2: Build the prompt request with the retrieved context
        context = "\n\n".join(chunk.content for chunk in retrieved_chunks)
        prompt_request = PromptRequest(
            question=request.query,
            context=context,
            history=history
        )

        # Step 3: Build chat messages using the PromptService
        messages = self.prompt_service.build_messages(prompt_request)

        return messages, retrieved_chunks

    async def ask(self, request: RAGRequest, history: list[ChatMessage] | None = None) -> RAGResponse:
        messages, retrieved_chunks = await self._build_messages(request, history=history)

        # Step 4: Send the messages to the LLM provider and get a response
        chat_response = await self.llm_provider.chat(messages)

        # Step 5: Return the RAGResponse containing the chat response and retrieved chunks
        return RAGResponse(response=chat_response, retrieved_chunks=retrieved_chunks)
    
    async def ask_stream(self, request: RAGRequest, history: list[ChatMessage] | None = None) -> RAGStreamResponse:
        messages, retrieved_chunks = await self._build_messages(request, history=history)

        # Step 4: Stream the response from the LLM provider
        async def stream_response():
            async for chunk in self.llm_provider.stream_chat(messages):
                yield chunk

        # Step 5: Return the RAGStreamResponse containing the streamed chunks and retrieved chunks
        return RAGStreamResponse(chunks=stream_response(), retrieved_chunks=retrieved_chunks)