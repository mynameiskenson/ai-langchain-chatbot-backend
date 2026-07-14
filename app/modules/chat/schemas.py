from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class ChatRequestSchema(BaseModel):
    query: str
    top_k: int = 5
    owner_id: Optional[str] = None


class RetrievedChunkSchema(BaseModel):
    document_id: UUID
    content: str
    chunk_index: int
    page_number: Optional[int]
    metadata: dict
    score: Optional[float]

    model_config = {"from_attributes": True}


class ChatResponseSchema(BaseModel):
    content: str
    model: str
    finish_reason: Optional[str]
    usage: Optional[dict]

    model_config = {"from_attributes": True}


class ChatResultSchema(BaseModel):
    response: ChatResponseSchema
    retrieved_chunks: List[RetrievedChunkSchema]

    model_config = {"from_attributes": True}
