"""NiceGUI integration setup for FastAPI"""

from fastapi import FastAPI
from nicegui import app as nicegui_app
from app.core.logging import app_logger

def setup_nicegui(app: FastAPI):
    """Set up NiceGUI integration with FastAPI"""
    try:
        # Mount NiceGUI static files
        nicegui_app.mount_to(app)
        app_logger.info("NiceGUI mounted to FastAPI successfully")
    except Exception as e:
        app_logger.error(f"Error setting up NiceGUI: {e}")
        raise

__all__ = ["setup_nicegui"]