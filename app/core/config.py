"""Application configuration using Pydantic Settings V2"""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = Field(default="HP Ecommerce Store")
    APP_DESCRIPTION: str = Field(default="Complete HP products ecommerce platform")
    APP_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=True)
    
    # Server
    HOST: str = Field(default="127.0.0.1")
    PORT: int = Field(default=8080)
    API_PREFIX: str = Field(default="/api")
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./data/hp_store.db")
    
    # Security
    SECRET_KEY: str = Field(default="hp-store-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # File uploads
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    UPLOAD_DIRECTORY: str = Field(default="./app/static/uploads")
    
    # Email (for order confirmations)
    SMTP_HOST: Optional[str] = Field(default=None)
    SMTP_PORT: int = Field(default=587)
    SMTP_USERNAME: Optional[str] = Field(default=None)
    SMTP_PASSWORD: Optional[str] = Field(default=None)
    
    # Payment (placeholder for future integration)
    STRIPE_PUBLIC_KEY: Optional[str] = Field(default=None)
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None)
    PAYPAL_CLIENT_ID: Optional[str] = Field(default=None)
    PAYPAL_CLIENT_SECRET: Optional[str] = Field(default=None)

settings = Settings()