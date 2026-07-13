from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    data: T | None = None
    message: str = "Request processed successfully."
    success: bool = True