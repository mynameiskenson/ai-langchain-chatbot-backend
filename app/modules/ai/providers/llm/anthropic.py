from app.core.config import settings

from app.modules.ai.providers.llm.base import LLMProvider
from app.modules.ai.providers.llm.dto import ChatMessage, ChatResponse, ChatStreamChunk

from langchain_anthropic import ChatAnthropic


class AnthropicLLMProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        # use nested settings under `ai`
        self.api_key = api_key or settings.ai.ANTHROPIC_API_KEY
        self.model = model or settings.ai.ANTHROPIC_MODEL
        self.client = ChatAnthropic(api_key=self.api_key, model=self.model)

    async def chat(self, messages: list[ChatMessage]) -> ChatResponse:
        """Send messages to Anthropic and return a `ChatResponse`."""
        payload = [{"role": m.role, "content": m.content} for m in messages]
        response = await self.client.ainvoke(payload)
        finish_reason = getattr(response, "response_metadata", {}).get("stop_reason")
        return ChatResponse(content=response.content, model=self.model, finish_reason=finish_reason)

    async def stream_chat(self, messages: list[ChatMessage]):
        """Stream response chunks from Anthropic."""
        payload = [{"role": m.role, "content": m.content} for m in messages]
        response_stream = self.client.astream(payload)
        async for chunk in response_stream:
            # LangChain only populates `response_metadata` (e.g. `stop_reason`)
            # on the final chunk of the stream, so use its presence to detect
            # completion instead of a non-existent `is_final` attribute.
            finish_reason = getattr(chunk, "response_metadata", {}).get("stop_reason")
            yield ChatStreamChunk(
                content=chunk.content,
                model=self.model,
                finish_reason=finish_reason,
                is_final=finish_reason is not None,
            )