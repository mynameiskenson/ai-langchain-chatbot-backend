from app.modules.ai.constant import AIProviderType

from app.modules.ai.providers.llm.anthropic import AnthropicLLMProvider
from app.modules.ai.providers.llm.base import LLMProvider
from app.core.config import settings

class LLMFactory:
    @staticmethod
    def create(provider: str) -> LLMProvider:
        provider = provider.lower()
        match provider:
            case AIProviderType.ANTHROPIC.value:
                return AnthropicLLMProvider()
            case _:
                raise ValueError(f"Unsupported LLM provider: {provider}")