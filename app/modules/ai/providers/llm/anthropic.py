from app.core.config import settings

from app.modules.ai.providers.llm.base import LLMProvider
from app.modules.ai.providers.llm.dto import ChatMessage, ChatResponse

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
        return ChatResponse(content=response.content, model=self.model, finish_reason=getattr(response, "finish_reason", None))

    async def stream_chat(self, messages: list[ChatMessage]):
        """Stream response chunks from Anthropic."""
        payload = [{"role": m.role, "content": m.content} for m in messages]
        async for chunk in self.client.ainvoke_stream(payload):
            yield chunk.content