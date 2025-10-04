import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("uvicorn")  # Use uvicorn logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger.info(f"Request: {request.method} - {request.url}")
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
