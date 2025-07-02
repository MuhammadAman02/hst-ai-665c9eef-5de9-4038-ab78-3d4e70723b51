@echo off
echo ===================================================
echo FastAPI + NiceGUI Project Setup and Run
echo ===================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment already exists.
)

:: Activate virtual environment and install dependencies
echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

:: Verify critical dependencies
echo Verifying critical dependencies...
python -c "import uvicorn, fastapi, nicegui; print('Dependencies successfully installed!')" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Critical dependencies are missing.
    echo Please check the error messages above and try again.
    pause
    exit /b 1
)

echo All dependencies installed successfully!
echo.

:: Ask user if they want to run the application
set /p RUN_APP=Do you want to run the application now? (Y/N): 

if /i "%RUN_APP%"=="Y" (
    echo.
    echo Starting the application...
    echo.
    echo The application will be available at: http://localhost:8000
    echo The NiceGUI UI will be available at: http://localhost:8000/ui
    echo.
    echo Press Ctrl+C to stop the application.
    echo.
    python main.py
) else (
    echo.
    echo To run the application later, use one of these commands:
    echo   - python main.py
    echo   - python -m uvicorn main:app --reload
    echo.
    echo Make sure to activate the virtual environment first with:
    echo   venv\Scripts\activate
)

pause