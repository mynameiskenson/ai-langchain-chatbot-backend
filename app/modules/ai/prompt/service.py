from typing import List

from app.modules.ai.prompt.dto import PromptRequest
from app.modules.ai.prompt.template import SYSTEM_PROMPT
from app.modules.ai.providers.llm.dto import ChatMessage



class PromptService:
	"""Create a list of `ChatMessage` objects from a `PromptRequest`.

	The returned list is in this order:
	- System message (instructions + retrieved context)
	- Conversation history (kept as-is)
	- User message (the current question)
	"""


	def _format_context_block(self, context: str) -> str:
		"""Format retrieved context into a readable block.

		Returns an empty string when there is no context.
		"""
		if not context or not context.strip():
			return ""

		return (
			"Retrieved Documents\n"
			"-------------------\n\n"
			f"{context.strip()}"
		)


	def _build_system_content(self, context: str) -> str:
		"""Join the system prompt and the formatted context into one string.

		If there is no context, returns only the system prompt.
		"""
		parts: List[str] = [SYSTEM_PROMPT.strip()]
		ctx_block = self._format_context_block(context)
		if ctx_block:
			parts.append(ctx_block)
		return "\n\n".join(parts)


	def build_messages(self, request: PromptRequest) -> List[ChatMessage]:
		"""Return chat messages ready for an LLM provider.

		Simple steps:
		1. Make the system message (instructions + context).
		2. Add any past conversation messages unchanged.
		3. Add the user's current question as the last message.
		"""
		system_content = self._build_system_content(request.context)
		messages: List[ChatMessage] = [ChatMessage(role="system", content=system_content)]

		# Append history messages unchanged
		if request.history:
			messages.extend(request.history)

		# Append the current user question
		messages.append(ChatMessage(role="user", content=request.question))

		return messages
