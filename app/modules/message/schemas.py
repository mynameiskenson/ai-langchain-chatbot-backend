from uuid import UUID

from pydantic import BaseModel

class MessageResponseSchema(BaseModel):
    id: UUID
    conversation_id: str
    content: str
    role: str
    model_config = {"from_attributes": True}