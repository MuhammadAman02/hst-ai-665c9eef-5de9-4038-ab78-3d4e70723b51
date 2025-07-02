from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from typing import Dict, List, Optional, Union, Any, Callable
import traceback

from app.core.exceptions import AppException, ErrorDetail
from app.core.logging import app_logger

def setup_error_handlers(app: FastAPI) -> None:
    """Set up global exception handlers for the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        app_logger.error(
            f"AppException caught: {exc.name} - {exc.detail}",
            extra={"request_url": str(request.url), "status_code": exc.status_code}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "name": exc.name},
            headers=exc.headers
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        app_logger.error(
            f"Request validation error: {exc.errors()}",
            extra={"request_url": str(request.url), "body": exc.body}
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors(), "body": exc.body},
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        app_logger.error(
            f"Pydantic validation error: {exc.errors()}",
            extra={"request_url": str(request.url)}
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        app_logger.exception(
            f"Unhandled exception: {exc}",
            extra={"request_url": str(request.url)}
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred."},
        )

def create_error_response(
    status_code: int, 
    detail: Union[str, List[ErrorDetail]],
    headers: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized error response.
    
    Args:
        status_code: HTTP status code
        detail: Error detail message or list of error details
        headers: Optional response headers
        
    Returns:
        JSONResponse with standardized error format
    """
    if isinstance(detail, str):
        content = {"detail": detail}
    else:
        content = {"detail": [error.dict() for error in detail]}
    
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=headers,
    )

def with_error_handling(func: Callable) -> Callable:
    """Decorator to add error handling to any function.
    
    This decorator catches exceptions and logs them appropriately.
    It can be used for non-FastAPI functions that need error handling.
    
    Args:
        func: The function to wrap with error handling
        
    Returns:
        Wrapped function with error handling
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppException as exc:
            app_logger.error(f"AppException in {func.__name__}: {exc.detail}")
            raise
        except Exception as exc:
            app_logger.error(
                f"Unhandled exception in {func.__name__}: {str(exc)}",
                extra={"traceback": traceback.format_exc()}
            )
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later."
            )
    
    return wrapper