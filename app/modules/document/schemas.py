from uuid import UUID

from pydantic import BaseModel

class DocumentResponseSchema(BaseModel):
    id: UUID
    original_filename: str
    mime_type: str
    file_size: int
    user_id: str
    status: str
    model_config = {"from_attributes": True}