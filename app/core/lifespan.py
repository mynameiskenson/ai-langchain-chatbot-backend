from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    This function is used to manage the lifespan of the FastAPI application.
    It can be used to perform setup and teardown tasks when the application starts and stops.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    try:
        # Perform setup tasks here
        logger.info("Chatbot Backend is starting up...")
        yield
    finally:
        # Perform teardown tasks here
        logger.info("Chatbot Backend is shutting down...")