from fastapi import APIRouter

from app.core.exceptions import ApplicationError

error_router = APIRouter()

@error_router.get("/error", summary="Test Error Handling", description="Endpoint to test error handling by raising a custom ApplicationError.")
def error_check():
    raise ApplicationError("This is a test error.")

@error_router.get("/crash", summary="Test Crash Handling", description="Endpoint to test crash handling by raising a ZeroDivisionError.")
def crash_check():
    x = 1 / 0
    return x