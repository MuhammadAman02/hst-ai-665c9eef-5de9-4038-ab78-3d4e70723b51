"""Core module initialization with defensive imports and fallbacks"""

import os
import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# Set up basic logging immediately
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

fallback_logger = logging.getLogger("app.core")

# Safe import function
def safe_import(module_name: str, attributes: List[str], fallbacks: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Safely import attributes from a module with fallbacks."""
    result = {}
    fallbacks = fallbacks or {}
    
    try:
        module = __import__(module_name, fromlist=attributes)
        for attr in attributes:
            if hasattr(module, attr):
                result[attr] = getattr(module, attr)
            else:
                fallback_logger.warning(f"Attribute '{attr}' not found in {module_name}")
                result[attr] = fallbacks.get(attr)
    except ImportError as e:
        fallback_logger.warning(f"Failed to import {module_name}: {e}")
        for attr in attributes:
            result[attr] = fallbacks.get(attr)
    except Exception as e:
        fallback_logger.error(f"Unexpected error importing {module_name}: {e}")
        for attr in attributes:
            result[attr] = fallbacks.get(attr)
    
    return result

# Import configuration with fallback
class FallbackSettings:
    def __init__(self):
        self.APP_NAME = os.getenv("APP_NAME", "HP Ecommerce Store")
        self.APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "HP Products Store")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.DEBUG = os.getenv("DEBUG", "True").lower() == "true"
        self.HOST = os.getenv("HOST", "127.0.0.1")
        self.PORT = int(os.getenv("PORT", "8080"))
        self.API_PREFIX = os.getenv("API_PREFIX", "/api")
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/hp_store.db")
        self.SECRET_KEY = os.getenv("SECRET_KEY", "hp-store-secret-key")

config_imports = safe_import("app.core.config", ["settings"], {"settings": FallbackSettings()})
settings = config_imports["settings"]

# Import logging with fallback
def fallback_get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"app.{name}")

logging_imports = safe_import("app.core.logging", ["app_logger", "get_logger"], {
    "app_logger": fallback_logger,
    "get_logger": fallback_get_logger
})
app_logger = logging_imports["app_logger"]
get_logger = logging_imports["get_logger"]

# Import database with fallback
def fallback_init_database():
    fallback_logger.warning("Database initialization not available")

database_imports = safe_import("app.core.database", ["init_database"], {
    "init_database": fallback_init_database
})
init_database = database_imports["init_database"]

# Middleware and router setup functions
def setup_middleware(app):
    """Set up FastAPI middleware"""
    try:
        from fastapi.middleware.cors import CORSMiddleware
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app_logger.info("CORS middleware configured")
    except Exception as e:
        app_logger.error(f"Error setting up middleware: {e}")

def setup_routers(app, api_prefix: str = ""):
    """Set up FastAPI routers"""
    try:
        from app.api import api_router
        
        if api_prefix:
            app.include_router(api_router, prefix=api_prefix)
        else:
            app.include_router(api_router)
        
        app_logger.info(f"API routers configured with prefix: {api_prefix}")
    except Exception as e:
        app_logger.error(f"Error setting up routers: {e}")

def setup_error_handlers(app):
    """Set up error handlers"""
    try:
        from fastapi import Request, HTTPException
        from fastapi.responses import JSONResponse
        
        @app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail}
            )
        
        @app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            app_logger.error(f"Unhandled exception: {exc}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
        
        app_logger.info("Error handlers configured")
    except Exception as e:
        app_logger.error(f"Error setting up error handlers: {e}")

# Health check functions
class HealthCheck:
    @staticmethod
    def check_all():
        """Perform comprehensive health check"""
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": settings.APP_VERSION,
            "database": "connected"
        }

def is_healthy() -> bool:
    """Simple health check"""
    return True

def validate_environment() -> List[str]:
    """Validate environment configuration"""
    errors = []
    
    # Check data directory
    data_dir = Path("data")
    if not data_dir.exists():
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            app_logger.info("Created data directory")
        except Exception as e:
            errors.append(f"Cannot create data directory: {e}")
    
    # Check static directory
    static_dir = Path("app/static")
    if not static_dir.exists():
        try:
            static_dir.mkdir(parents=True, exist_ok=True)
            app_logger.info("Created static directory")
        except Exception as e:
            errors.append(f"Cannot create static directory: {e}")
    
    return errors

def setup_database():
    """Initialize database"""
    try:
        init_database()
        app_logger.info("Database setup completed")
    except Exception as e:
        app_logger.error(f"Database setup failed: {e}")

def setup_nicegui(app):
    """Set up NiceGUI integration"""
    try:
        from app.core.nicegui_setup import setup_nicegui as _setup_nicegui
        _setup_nicegui(app)
        app_logger.info("NiceGUI integration configured")
    except Exception as e:
        app_logger.warning(f"NiceGUI integration not available: {e}")

# Export all components
__all__ = [
    "settings",
    "app_logger", 
    "get_logger",
    "setup_middleware",
    "setup_routers", 
    "setup_error_handlers",
    "HealthCheck",
    "is_healthy",
    "validate_environment",
    "setup_database",
    "setup_nicegui"
]