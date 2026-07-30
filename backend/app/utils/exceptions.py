"""Custom application exceptions and their FastAPI exception handlers."""
import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base class for all application-specific exceptions."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InvalidImageException(AppException):
    def __init__(self, message: str = "The uploaded file is not a valid image."):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class UnsupportedFormatException(AppException):
    def __init__(self, message: str = "Unsupported image format. Allowed formats: JPG, JPEG, PNG."):
        super().__init__(message, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


class CorruptedImageException(AppException):
    def __init__(self, message: str = "The uploaded image appears to be corrupted."):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_CONTENT)


class ImageTooLargeException(AppException):
    def __init__(self, message: str = "The uploaded image exceeds the maximum allowed size."):
        super().__init__(message, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)


class ModelLoadException(AppException):
    def __init__(self, message: str = "Failed to load the prediction model."):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE)


class ModelNotLoadedException(AppException):
    def __init__(self, message: str = "The prediction model is not ready yet."):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE)


class PredictionException(AppException):
    def __init__(self, message: str = "An error occurred while generating the prediction."):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class DiseaseInfoNotFoundException(AppException):
    def __init__(self, class_name: str):
        super().__init__(
            f"No recommendation data found for class '{class_name}'.",
            status.HTTP_404_NOT_FOUND,
        )


class DatabaseConnectionException(AppException):
    def __init__(self, message: str = "Failed to connect to the database."):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE)


class HistoryNotFoundException(AppException):
    def __init__(self, record_id: str):
        super().__init__(f"No history record found with id '{record_id}'.", status.HTTP_404_NOT_FOUND)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global exception handlers so every AppException returns a consistent JSON body."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning("AppException on %s: %s", request.url.path, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.__class__.__name__, "message": exc.message},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s", request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "InternalServerError", "message": "An unexpected error occurred."},
        )
