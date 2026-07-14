from abc import ABC, abstractmethod

from app.modules.ai.providers.llm.dto import ChatMessage, ChatResponse

class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[ChatMessage]) -> ChatResponse:
        """Send chat messages and return the provider's response."""
        pass
    
    @abstractmethod
    async def stream_chat(self, messages: list[ChatMessage]):
        """Send chat messages and yield response chunks."""
        pass