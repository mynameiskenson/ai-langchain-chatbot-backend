from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup and shutdown actions for the FastAPI app."""
    try:
        # Perform setup tasks here
        logger.info("Chatbot Backend is starting up...")
        yield
    finally:
        # Perform teardown tasks here
        logger.info("Chatbot Backend is shutting down...")