import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.errors import AppError

logger = logging.getLogger("hms")


def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        logger.warning("app_error", extra={
            "code": exc.code, "path": request.url.path,
            "request_id": getattr(request.state, "request_id", None),
        })
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "code": "INVALID_REQUEST",
                "message": "Request validation failed.",
                "details": {"errors": exc.errors()},
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception", exc_info=exc, extra={
            "path": request.url.path,
            "request_id": getattr(request.state, "request_id", None),
        })
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "details": {},
            },
        )
