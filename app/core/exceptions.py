import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette import status

logger = logging.getLogger(__name__)


class InvalidRFIDFileError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidRFIDFileError)
    async def invalid_file_handler(_: Request, exc: InvalidRFIDFileError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": "error", "message": exc.message},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        """Explicit handler so HTTPException is never swallowed by the catch-all below."""
        content: dict = {"status": "error", "message": exc.detail}
        headers = getattr(exc, "headers", None)
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=headers,
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": "Unexpected server error"},
        )
