from uuid import UUID

from pydantic import BaseModel

class ConversationCreateSchema(BaseModel):
    title: str
    user_id: str

class ConversationResponseSchema(BaseModel):
    id: UUID
    title: str
    user_id: str
    status: str
    model_config = {"from_attributes": True}