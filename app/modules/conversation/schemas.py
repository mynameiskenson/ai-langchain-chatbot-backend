from uuid import UUID

from pydantic import BaseModel

class ConversationCreateSchema(BaseModel):
    title: str
    owner_id: str

class ConversationResponseSchema(BaseModel):
    id: UUID
    title: str
    owner_id: str
    status: str
    model_config = {"from_attributes": True}