import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from pydantic import AnyHttpUrl, field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Core Application Settings
    APP_NAME: str = "ProjectBase"
    APP_DESCRIPTION: str = "A modular Python web application template"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False # Set to True for development, False for production

    # Server Settings
    HOST: str = "0.0.0.0" # Use 0.0.0.0 for Docker/production
    PORT: int = 8000
    API_PREFIX: str = "/api"
    NICEGUI_MOUNT_PATH: str = "/" # Path where NiceGUI will be mounted

    # CORS Settings
    # Comma-separated list of origins, e.g.: http://localhost:3000,https://example.com
    CORS_ORIGINS: str = ""
    CORS_ORIGINS_LIST: List[str] = []

    # Security Settings (for authentication/authorization)
    ENABLE_AUTH: bool = False # Feature flag to enable/disable authentication
    SECRET_KEY: str = "your_super_secret_key_replace_me" # Generate a strong key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database Settings (for SQLAlchemy/ORM)
    ENABLE_DATABASE: bool = False # Feature flag to enable/disable database
    DATABASE_URL: Optional[str] = None # e.g., "sqlite:///./test.db" or "postgresql://user:pass@host/db"

    # Static Files and Templates
    STATIC_DIR: Path = Path("app/static")
    TEMPLATES_DIR: Path = Path("app/templates")

    # Logging Settings
    LOG_LEVEL: str = "INFO" # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_TO_FILE: bool = False
    LOG_FILE: str = "logs/app.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'




settings = Settings()

# Manually parse CORS_ORIGINS after settings are loaded
if settings.CORS_ORIGINS.lower() == "*":
    settings.CORS_ORIGINS_LIST = ["*"]
else:
    settings.CORS_ORIGINS_LIST = [i.strip() for i in settings.CORS_ORIGINS.split(",") if i.strip()]

# Helper function to get settings as a dictionary
def get_settings_dict() -> Dict[str, Any]:
    """Return settings as a dictionary for easy access."""
    return settings.model_dump()

# Helper function to get a specific setting
def get_setting(key: str, default: Any = None) -> Any:
    """Get a specific setting by key with an optional default value."""
    return getattr(settings, key, default)