@echo off
echo ===================================================
echo   IstanteS7 - Build Standalone Portable EXE
echo ===================================================
echo.

if not exist venv (
    echo [ERROR] Virtual environment not found. Please run run.bat first to set up dependencies.
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Installing PyInstaller...
pip install pyinstaller

echo [INFO] Building standalone executable with PyInstaller...
:: Using pyinstaller with options:
:: --onefile: produce a single executable file
:: --noconsole: do not show command prompt window behind GUI
:: --clean: clean PyInstaller cache before building
:: --name: name of the output executable
:: --add-data: if we had asset folders, we would add them here.
pyinstaller --onefile --noconsole --clean --name="IstanteS7" src/main.py

if %errorlevel% eq 0 (
    echo.
    echo ===================================================
    echo   [SUCCESS] Build complete!
    echo   The portable executable is located in:
    echo   %CD%\dist\IstanteS7.exe
    echo ===================================================
) else (
    echo.
    echo [ERROR] Build failed with code %errorlevel%.
)

pause
