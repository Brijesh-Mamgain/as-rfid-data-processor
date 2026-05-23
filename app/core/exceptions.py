from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status


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

    @app.exception_handler(Exception)
    async def generic_error_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": "Unexpected server error"},
        )
