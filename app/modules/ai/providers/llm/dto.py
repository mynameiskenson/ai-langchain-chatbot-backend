from dataclasses import dataclass

@dataclass(slots=True)
class ChatMessage:
    role: str
    content: str

@dataclass(slots=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

@dataclass(slots=True)
class ChatResponse:
    content: str
    model: str
    finish_reason: str | None
    usage: TokenUsage | None = None