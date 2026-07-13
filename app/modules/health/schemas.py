from pydantic import BaseModel

class HealthCheckResponse(BaseModel):
    status: str = "healthy"

class DatabaseHealthCheckResponse(BaseModel):
    status: str = "healthy"
    database: str = "connected"