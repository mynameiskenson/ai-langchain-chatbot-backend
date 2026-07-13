import logging
import time

from fastapi import Request

logger = logging.getLogger(__name__)

async def log_request(request: Request, call_next):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Error processing request: {e} - {request.method} {request.url.path}")
        raise e
    
    process_time = (time.perf_counter() - start_time) * 1000

    logger.info(
        f"Request: {request.method} {request.url.path} | "
        f"Status Code: {response.status_code} | "
        f"Process Time: {process_time:.4f}s"
    )

    return response