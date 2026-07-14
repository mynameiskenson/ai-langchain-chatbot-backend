from dataclasses import dataclass

from app.modules.ai.providers.llm.dto import ChatMessage

@dataclass(slots=True)
class PromptRequest:
    """Request data for building prompt messages.

    Fields: question, context, history
    """
    question: str
    context: str
    history: list[ChatMessage]