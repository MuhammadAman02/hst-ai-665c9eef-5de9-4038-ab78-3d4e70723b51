import time
from typing import Dict, List, Optional, Set

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.logging import app_logger

def setup_middleware(app: FastAPI) -> None:
    """Set up global middleware for the FastAPI application."""

    # CORS Middleware
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app_logger.info(f"CORS middleware enabled for origins: {settings.CORS_ORIGINS}")
    else:
        app_logger.warning("CORS_ORIGINS not set. CORS middleware is disabled.")

    # GZip Middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app_logger.info("GZip middleware enabled.")

    # Session Middleware (only if authentication is enabled and secret key is provided)
    if settings.ENABLE_AUTH and settings.SECRET_KEY:
        app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
        app_logger.info("Session middleware enabled.")
    elif settings.ENABLE_AUTH and not settings.SECRET_KEY:
        app_logger.warning("SECRET_KEY not set. Session middleware disabled despite ENABLE_AUTH.")
    else:
        app_logger.info("Session middleware disabled as authentication is not enabled.")

    # Request Timing Middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        app_logger.debug(f"Request processed in {process_time:.4f} seconds.",
                         extra={"path": request.url.path, "method": request.method, "process_time": process_time})
        return response
    app_logger.info("Request timing middleware enabled.")

# Custom middleware classes

class RateLimitMiddleware:
    """Simple rate limiting middleware.
    
    This is a basic implementation. For production, consider using a more
    robust solution with Redis or another distributed cache.
    """
    def __init__(
        self,
        app,
        limit: int = 100,
        window: int = 60,
        exempt_paths: List[str] = None,
    ):
        self.app = app
        self.limit = limit  # requests per window
        self.window = window  # window in seconds
        self.exempt_paths = exempt_paths or []
        self.requests = {}
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        # Get client IP
        client_ip = self._get_client_ip(scope)
        path = scope["path"]
        
        # Skip rate limiting for exempt paths
        if any(path.startswith(exempt) for exempt in self.exempt_paths):
            return await self.app(scope, receive, send)
        
        # Check rate limit
        current_time = time.time()
        if client_ip in self.requests:
            requests_info = self.requests[client_ip]
            # Clean up old requests
            requests_info = [r for r in requests_info if current_time - r < self.window]
            
            if len(requests_info) >= self.limit:
                # Rate limit exceeded
                return await self._rate_limit_response(scope, receive, send)
            
            requests_info.append(current_time)
            self.requests[client_ip] = requests_info
        else:
            self.requests[client_ip] = [current_time]
        
        return await self.app(scope, receive, send)
    
    def _get_client_ip(self, scope):
        """Extract client IP from scope."""
        headers = dict(scope.get("headers", []))
        forwarded = headers.get(b"x-forwarded-for", b"").decode("utf8").split(",")[0].strip()
        if forwarded:
            return forwarded
        return scope.get("client", ("", 0))[0] or "unknown"
    
    async def _rate_limit_response(self, scope, receive, send):
        """Send rate limit exceeded response."""
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                [b"content-type", b"application/json"],
                [b"retry-after", str(self.window).encode()],
            ],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"detail":"Rate limit exceeded. Please try again later."}',
        })

# Helper function to add rate limiting
def add_rate_limiting(app: FastAPI, limit: int = 100, window: int = 60, exempt_paths: List[str] = None) -> None:
    """Add rate limiting middleware to the application.
    
    Args:
        app: The FastAPI application
        limit: Maximum number of requests per window
        window: Time window in seconds
        exempt_paths: List of path prefixes to exempt from rate limiting
    """
    app.add_middleware(
        RateLimitMiddleware,
        limit=limit,
        window=window,
        exempt_paths=exempt_paths or ["/static", "/docs", "/redoc", "/openapi.json"],
    )
    app_logger.info(f"Rate limiting configured: {limit} requests per {window} seconds")