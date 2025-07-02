"""Logging configuration for the application"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Any

# Ensure logs directory exists
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Create application logger
app_logger = logging.getLogger("app")
app_logger.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
app_logger.addHandler(console_handler)

# File handler
try:
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    file_handler.setFormatter(formatter)
    app_logger.addHandler(file_handler)
except Exception as e:
    app_logger.error(f"Failed to set up file logging: {e}")

# Set log level from environment
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
if log_level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
    app_logger.setLevel(getattr(logging, log_level))

def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module"""
    logger = logging.getLogger(f"app.{name}")
    logger.setLevel(app_logger.level)
    
    if not logger.handlers:
        logger.addHandler(console_handler)
        if 'file_handler' in locals():
            logger.addHandler(file_handler)
    
    return logger

def log_structured(logger: logging.Logger, level: str, message: str, data: Dict[str, Any]) -> None:
    """Log a message with structured data"""
    try:
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(f"{message} - {data}")
    except Exception as e:
        logger.error(f"Error in log_structured: {e}")

# Export all logging components
__all__ = ["app_logger", "get_logger", "log_structured"]