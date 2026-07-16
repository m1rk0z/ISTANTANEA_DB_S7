@echo off
echo ===================================================
echo   IstanteS7 - Siemens PLC DB Backup Bootstrap
echo ===================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10 or newer from https://www.python.org/
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo [INFO] Creating Python virtual environment (venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment and install dependencies
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Checking and installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo [INFO] Launching IstanteS7...
python src/main.py
if %errorlevel% neq 0 (
    echo [WARNING] Application exited with code %errorlevel%.
)

pause
