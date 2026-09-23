from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import structlog

from src.exceptions.exceptions import AppException

logger = structlog.get_logger(__name__)


def get_request_id(request: Request) -> str:
    """Get the request ID assigned by middleware."""
    return getattr(
        request.state,
        "request_id",
        "unknown",
    )


async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    request_id = get_request_id(request)

    logger.warning(
        "application_error",
        error_code=exc.code,
        status_code=exc.status_code,
        request_id=request_id,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": request_id,
            },
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    request_id = get_request_id(request)

    logger.info(
        "request_validation_failed",
        request_id=request_id,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "request_id": request_id,
            },
        },
    )


async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    request_id = get_request_id(request)

    logger.exception(
        "unhandled_application_error",
        request_id=request_id,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
                "request_id": request_id,
            },
        },
    )