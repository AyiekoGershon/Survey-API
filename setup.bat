@echo off
REM Setup script for Sky Survey API (Windows)

echo.
echo Sky Survey API - Setup Script
echo ==============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [OK] Python found

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] pip is not installed. Please install pip.
    pause
    exit /b 1
)

echo [OK] pip found

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo [OK] Setup complete!
echo.
echo Next steps:
echo 1. Update .env file with your MySQL credentials
echo 2. Run: mysql -u root -p < database_schema.sql
echo 3. Run: uvicorn app.main:app --reload
echo.
echo API will be available at: http://localhost:8000
echo Swagger UI: http://localhost:8000/docs
echo.
pause
