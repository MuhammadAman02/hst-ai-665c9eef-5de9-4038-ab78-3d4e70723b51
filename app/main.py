from nicegui import ui
from fastapi import Depends
import asyncio
import json

from app.core import app_logger, settings

# Define the main UI page
@ui.page('/')
def main_page():
    with ui.card().classes('w-full max-w-3xl mx-auto my-6'):
        ui.label(settings.APP_NAME).classes('text-2xl font-bold mb-4')
        ui.markdown(f'''
        ## Welcome to {settings.APP_NAME}!
        
        This is a modern Python application built with:
        - **NiceGUI** for the frontend
        - **FastAPI** for the API
        - **Pydantic** for data validation
        
        ### Features
        - Modern, responsive UI
        - RESTful API endpoints
        - JWT authentication
        - Comprehensive error handling
        - Logging and monitoring
        - Docker and Fly.io deployment
        ''')
        
        ui.separator()
        
        with ui.row().classes('w-full justify-center gap-4 mt-4'):
            ui.button('API Documentation', on_click=lambda: ui.open(f'{settings.api_prefix}/docs' if settings.api_prefix else '/docs'))
            ui.button('GitHub', on_click=lambda: ui.open('https://github.com'))
            ui.button('About', on_click=lambda: ui.open('/about'))

# About page
@ui.page('/about')
def about_page():
    with ui.card().classes('w-full max-w-3xl mx-auto my-6'):
        ui.label('About').classes('text-2xl font-bold mb-4')
        ui.markdown(f'''
        ## About {settings.APP_NAME}
        
        This application was built as a modern Python web application template.
        It demonstrates best practices for building web applications with NiceGUI and FastAPI.
        
        ### Core Modules
        - **API**: RESTful endpoints with FastAPI
        - **Frontend**: UI components with NiceGUI
        - **Models**: Data validation with Pydantic
        - **Services**: Business logic and external integrations
        - **Core**: Configuration, logging, security, and utilities
        
        ### Deployment
        The application is designed to be deployed to Fly.io or any Docker-compatible platform.
        ''')
        
        with ui.row().classes('w-full justify-center mt-4'):
            ui.button('Back to Home', on_click=lambda: ui.navigate('/'))



# Define a health check page for Fly.io
@ui.page('/health')
def health_check_page():
    # Fly.io health checks typically look for a 200 OK status.
    # This page will return 200 OK. Content can be simple.
    ui.label('{"status": "healthy"}')



# Note: No ui.run() here. 
# This file only defines the UI pages and elements.
# The actual server will be started by project_base/main.py