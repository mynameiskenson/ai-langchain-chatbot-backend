from fastapi import FastAPI

from app.core.logging import setup_logging
from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.exceptions import register_exception_handlers

from app.middleware.logging import log_request

from app.router import api_router

from app.modules.system.schemas import RootResponse
from app.schemas.response import ApiResponse

setup_logging()

app = FastAPI(
    title=settings.app.APP_NAME,
    description=settings.app.APP_DESCRIPTION,
    version=settings.app.APP_VERSION,
    lifespan=lifespan
)

register_exception_handlers(app)

app.middleware("http")(log_request)

app.include_router(api_router)

@app.get("/", response_model=ApiResponse[RootResponse], summary="Root Endpoint", description="Get basic information about the backend service.")
async def read_root():
    return ApiResponse(data=RootResponse(
        app_name=settings.app.APP_NAME,
        app_version=settings.app.APP_VERSION,
        anthropic_api_model=settings.ai.ANTHROPIC_MODEL,
        message="Backend is running successfully!"
    ))