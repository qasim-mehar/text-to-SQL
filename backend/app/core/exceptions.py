from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc), "type": "validation_error"},
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "type": "internal_error"},
    )


async def sql_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"SQL error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "type": "sql_error"},
    )
