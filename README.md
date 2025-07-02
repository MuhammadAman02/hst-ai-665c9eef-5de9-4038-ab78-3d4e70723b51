# HST AI Python Engineer Project Base (2025 Edition)

A modern, production-ready foundation for building Python web applications with best practices for 2025. This project base is designed to work seamlessly with the HST AI Python Engineer prompt.

## Features

- **Framework Flexibility**: Support for multiple UI frameworks (NiceGUI, FastAPI+Jinja2, ReactPy)
- **UI-First Development**: Prioritizes creating responsive, modern UIs before complex backend features
- **SQLAlchemy V2 Ready**: Updated database patterns using SQLAlchemy 2.0
- **Pydantic V2 Compatible**: Uses the latest Pydantic patterns for data validation
- **Docker Support**: Production-ready containerization with a multi-stage Dockerfile
- **Fly.io Optimized**: Includes a `fly.toml` for easy deployment with auto-scaling
- **Version Compatibility**: Carefully selected dependency versions to ensure stability
- **Environment Configuration**: Uses `.env` files with pydantic-settings for type-safe configuration

## Project Structure

```
project_base/
├── app/
│   ├── __init__.py
│   ├── api/            # API endpoints (e.g., FastAPI routers)
│   │   └── __init__.py
│   ├── core/           # Core configuration, settings, error handling, logging
│   │   └── __init__.py
│   ├── frontend/       # UI implementations (e.g., NiceGUI pages, ReactPy components, FastAPI routes)
│   │   ├── __init__.py
│   │   # ├── nicegui_app.py  # Example: NiceGUI implementation
│   │   # ├── reactpy_app.py  # Example: ReactPy implementation
│   │   # └── routes.py       # Example: FastAPI frontend routes
│   ├── generated/      # AI-generated application code
│   │   └── __init__.py
│   ├── models/         # Data models & schemas (e.g., Pydantic, SQLAlchemy)
│   │   └── __init__.py
│   ├── services/       # Business logic & external API integrations
│   │   └── __init__.py
│   ├── static/         # Static assets (CSS, JS, images). ALL image files MUST be placed here or in subdirectories within static/. Do NOT create separate top-level image directories like 'pictures/'.
│   ├── templates/      # HTML templates (Jinja2)
│   └── main.py         # Defines FastAPI routes and application logic for the 'app' module
├── .dockerignore         # Specifies intentionally untracked files for Docker
├── .env                  # Environment variables (create this file based on .env.example if provided)
├── Dockerfile            # Container configuration
├── fly.toml              # fly.io deployment configuration
├── main.py               # Application entry point (runs the Uvicorn server)
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.8+
- Docker (optional, for containerized deployment)
- Fly.io account and `flyctl` CLI (optional, for Fly.io deployment)

### Installation

#### Dependency Compatibility

**Important Note**: This project has specific version requirements to ensure compatibility:

- **NiceGUI 1.4.21-1.4.24** requires **FastAPI >=0.109.1,<0.110.0**
- If you need to use a newer FastAPI version (>=0.115.0), you'll need to upgrade to NiceGUI 2.0+ when available

The requirements.txt file has been configured with compatible versions. Do not modify these version constraints unless you're prepared to resolve dependency conflicts.

#### Automatic Setup (Recommended)

1. Clone the repository
2. Run the appropriate setup script for your operating system:

   **Windows:**
   ```
   setup_and_run.bat
   ```

   **Unix/MacOS:**
   ```
   chmod +x setup_and_run.sh
   ./setup_and_run.sh
   ```

   **Alternative (All platforms):**
   ```
   python setup.py
   ```

   These scripts will:
   - Check your Python version
   - Create a virtual environment
   - Install all dependencies
   - Verify critical dependencies
   - Provide activation instructions
   - Optionally run the application

#### Manual Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```
     source venv/bin/activate
     ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Verify installation:
   ```
   python -c "import uvicorn, fastapi, nicegui; print('Dependencies successfully installed!')"
   ```

#### Troubleshooting

##### "uvicorn: command not found" Error

If you encounter this error when running the application, it means the `uvicorn` command is not in your PATH. This typically happens when:

1. The virtual environment is not activated
2. The `uvicorn` package was not installed correctly

**Solution:**

1. Ensure your virtual environment is activated:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

2. Reinstall the dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application using the Python module syntax instead of the command:
   ```
   python -m uvicorn main:app --reload
   ```

4. **Create a `.env` file** in the `project_base` directory (you can copy `.env.example` if one exists and modify it). At a minimum, it might look like this if you want to change the default port:
   ```env
   PORT=8000
   HOST=0.0.0.0
   ```
   If no `.env` file is present, the application will use default values (e.g., port 8000).

### Running the Application Locally

#### Method 1: Using main.py (Recommended)

1. **Ensure your virtual environment is activated:**
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

2. **Start the application:**
   ```bash
   python main.py
   ```

#### Method 2: Using uvicorn directly

1. **Ensure your virtual environment is activated:**
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

2. **Start the application using the uvicorn command:**
   ```bash
   uvicorn main:app --reload
   ```

   If you encounter a "uvicorn: command not found" error, use the Python module syntax instead:
   ```bash
   python -m uvicorn main:app --reload
   ```

#### Accessing the Application

- Open your browser and navigate to `http://localhost:8000` (or the port you specified in the `.env` file)
- The NiceGUI UI will be available at `http://localhost:8000/ui`

## API Endpoints

-   `GET /`: Returns a welcome message.
-   `GET /health`: Returns a health status, useful for monitoring.

## Deployment

### Docker Deployment

1.  **Build the Docker image:**
    ```bash
    docker build -t my-fastapi-app .
    ```
2.  **Run the Docker container:**
    ```bash
    docker run -p 8000:8000 -d my-fastapi-app
    ```
    Replace `8000:8000` with `<host_port>:<container_port>` if you need to map to a different host port. The container port is determined by the `PORT` environment variable set in the `Dockerfile` or `fly.toml` (defaulting to 8000).

### Fly.io Deployment

1.  **Install `flyctl`**: Follow the instructions at [fly.io/docs/hands-on/install-flyctl/](https://fly.io/docs/hands-on/install-flyctl/).
2.  **Login to Fly.io**: `fly auth login`
3.  **Launch the app (first time only)**:
    ```bash
    fly launch --name your-unique-app-name --region sin
    ```
    (Replace `your-unique-app-name` and `sin` (Singapore) with your desired app name and region. This will also create a `fly.toml` if one doesn't exist, or update the existing one.)
4.  **Deploy changes**:
    ```bash
    fly deploy
    ```

The `fly.toml` file is pre-configured for auto-scaling and to stop machines when idle to save costs.

## Customization

-   **Add new API endpoints**: Modify `project_base/app/main.py` to include new routes and logic.
-   **Modify dependencies**: Update `project_base/requirements.txt` and reinstall.
-   **Adjust Docker configuration**: Edit `project_base/Dockerfile`.
-   **Change deployment settings**: Update `project_base/fly.toml` for Fly.io.

## Core Principles for Development

While this base is minimal, consider these principles as you expand your application:

-   **Modularity**: Keep code organized into logical modules.
-   **Clarity**: Write clear, understandable code with type hints where appropriate.
-   **Testing**: Implement unit and integration tests for new features.
-   **Security**: Follow security best practices (input validation, authentication if needed, etc.).
-   **Documentation**: Keep this README and code comments up-to-date.