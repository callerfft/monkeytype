"""Application exceptions and global exception handlers."""

from typing import Any, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..models.error import ErrorResponse


class AppException(Exception):
    """Base application exception."""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class NotFoundError(AppException):
    """Resource not found (404)."""
    def __init__(self, message: str, code: str = "NOT_FOUND", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class SessionNotFoundError(NotFoundError):
    """Session not found (404)."""
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session '{session_id}' not found or expired.",
            code="SESSION_NOT_FOUND",
        )


class ValidationError(AppException):
    """Validation or bad request error (400)."""
    def __init__(self, message: str, code: str = "VALIDATION_ERROR", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class UnauthorizedError(AppException):
    """Missing or invalid credentials (401)."""
    def __init__(self, message: str = "Unauthorized", code: str = "UNAUTHORIZED"):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class LLMTimeoutError(AppException):
    """LLM evaluation timeout exceeded (504)."""
    def __init__(self, message: str = "LLM evaluation timed out (> 3.0s SLA)"):
        super().__init__(
            message=message,
            code="LLM_TIMEOUT",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        )


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    """Format custom AppException into standardized ErrorResponse."""
    payload = ErrorResponse(
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=payload.model_dump(),
    )


async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """Format FastAPI RequestValidationError into standardized ErrorResponse."""
    clean_errors = []
    for err in exc.errors():
        clean_errors.append({
            "loc": list(err.get("loc", [])),
            "msg": str(err.get("msg", "")),
            "type": str(err.get("type", "")),
        })
    payload = ErrorResponse(
        code="VALIDATION_ERROR",
        message="Invalid request payload or query parameters.",
        details=clean_errors,
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=payload.model_dump(),
    )


async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Format generic Starlette HTTPException into standardized ErrorResponse."""
    code = "HTTP_ERROR"
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        code = "NOT_FOUND"
    elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
        code = "UNAUTHORIZED"
    elif exc.status_code == status.HTTP_400_BAD_REQUEST:
        code = "VALIDATION_ERROR"
    elif exc.status_code == status.HTTP_504_GATEWAY_TIMEOUT:
        code = "LLM_TIMEOUT"

    payload = ErrorResponse(
        code=code,
        message=str(exc.detail),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=payload.model_dump(),
    )
