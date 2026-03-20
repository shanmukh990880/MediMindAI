from fastapi import Request
from fastapi.responses import JSONResponse
from backend.models.api import ErrorResponse
import logging

logger = logging.getLogger(__name__)

class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

async def app_exception_handler(request: Request, exc: AppException):
    logger.warning(f"AppException [{exc.status_code}]: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=exc.message).model_dump()
    )

async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(detail="An unexpected internal server error occurred.").model_dump()
    )
