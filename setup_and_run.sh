#!/bin/bash

echo "==================================================="
echo "FastAPI + NiceGUI Project Setup and Run"
echo "==================================================="
echo 

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH."
    echo "Please install Python 3.8 or higher from https://www.python.org/downloads/"
    echo "or use your system's package manager."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "ERROR: Python 3.8 or higher is required."
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment."
        exit 1
    fi
    echo "Virtual environment created successfully."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies."
    exit 1
fi

# Verify critical dependencies
echo "Verifying critical dependencies..."
python -c "import uvicorn, fastapi, nicegui; print('Dependencies successfully installed!')" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Critical dependencies are missing."
    echo "Please check the error messages above and try again."
    exit 1
fi

echo "All dependencies installed successfully!"
echo

# Ask user if they want to run the application
read -p "Do you want to run the application now? (Y/N): " RUN_APP

if [[ $RUN_APP =~ ^[Yy]$ ]]; then
    echo
    echo "Starting the application..."
    echo
    echo "The application will be available at: http://localhost:8000"
    echo "The NiceGUI UI will be available at: http://localhost:8000/ui"
    echo
    echo "Press Ctrl+C to stop the application."
    echo
    python main.py
else
    echo
    echo "To run the application later, use one of these commands:"
    echo "  - python main.py"
    echo "  - python -m uvicorn main:app --reload"
    echo
    echo "Make sure to activate the virtual environment first with:"
    echo "  source venv/bin/activate"
fi