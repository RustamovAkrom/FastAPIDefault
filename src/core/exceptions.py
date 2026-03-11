from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.logger import configure_logger

logger = configure_logger()


class APIException(Exception):
    """
    Base exception for API errors.
    """

    status_code: int = 400
    default_code: str = "error"
    default_detail: str = "Something went wrong."

    def __init__(
        self,
        detail: str | None = None,
        code: str | None = None,
        values: dict[str, Any] | None = None,
        status_code: int | None = None,
    ) -> None:
        self.detail: str = detail or self.default_detail
        self.code: str = code or self.default_code
        self.values: dict[str, Any] = values or {}
        self.status_code: int = status_code or self.status_code

        super().__init__(self.detail)


class PermissionDeniedError(APIException):
    """
    Raised when user does not have permission.
    """

    status_code = 403
    default_code = "permission_denied"
    default_detail = "You do not have permission to perform this action."


class NotFoundError(APIException):
    """
    Raised when object is not found.
    """

    status_code = 404
    default_code = "not_found"
    default_detail = "Requested resource was not found."


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register exception handlers for the FastAPI application.
    """

    @app.exception_handler(APIException)
    async def api_exception_handler(
        request: Request,
        exc: APIException,
    ) -> JSONResponse:
        logger.warning(
            "APIException raised",
            extra={
                "path": request.url.path,
                "code": exc.code,
                "detail": exc.detail,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "code": exc.code,
                "variables": exc.values,
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unhandled exception",
            extra={"path": request.url.path},
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error.",
                "code": "internal_error",
            },
        )
