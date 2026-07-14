import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# ==========================================================
# Base Exception
# ==========================================================

class ApplicationError(Exception):
    """Base class for application-specific exceptions."""
    
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

# ==========================================================
# Custom Exception
# ==========================================================

class BadRequestException(ApplicationError):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, status_code=400)


class UnauthorizedException(ApplicationError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, status_code=401)


class ForbiddenException(ApplicationError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, status_code=403)


class NotFoundException(ApplicationError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)


class ConflictException(ApplicationError):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message=message, status_code=409)


class ValidationException(ApplicationError):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message=message, status_code=422)

async def app_exception_handler(request: Request, exc: ApplicationError):
    """Handle ApplicationError and return a JSON error response."""
    logger.error(f"ApplicationError: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message
            }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions and return a 500 JSON response."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unexpected error occurred."
        }
    )

def register_exception_handlers(app: FastAPI):
    """Attach custom exception handlers to the FastAPI app."""
    app.add_exception_handler(ApplicationError, app_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)