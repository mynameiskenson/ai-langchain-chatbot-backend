from app.modules.ai.prompt.service import PromptService
from app.modules.ai.prompt.dto import PromptRequest
from app.modules.ai.providers.llm.dto import ChatMessage
from app.modules.ai.prompt.template import SYSTEM_PROMPT


def test_build_messages_order_and_content():
    history = [
        ChatMessage(role="user", content="previous question"),
        ChatMessage(role="assistant", content="previous answer"),
    ]

    request = PromptRequest(
        question="What is X?",
        context="Document 1 content\n\nDocument 2 content",
        history=history,
    )

    svc = PromptService()
    msgs = svc.build_messages(request)

    # System message first
    assert len(msgs) >= 3
    assert msgs[0].role == "system"
    assert SYSTEM_PROMPT.strip() in msgs[0].content
    assert "Retrieved Documents" in msgs[0].content

    # History preserved
    assert msgs[1] == history[0]
    assert msgs[2] == history[1]

    # User question last
    assert msgs[-1].role == "user"
    assert msgs[-1].content == "What is X?"
