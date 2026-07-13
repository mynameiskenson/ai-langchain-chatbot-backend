from pydantic import BaseModel

class RootResponse(BaseModel):
    app_name: str
    app_version: str
    anthropic_api_model: str
    message: str