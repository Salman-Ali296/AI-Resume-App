@echo off
REM Setup script for Resume Analyzer (Windows)

echo === Resume Analyzer Setup ===

REM Check Python version
python --version

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Download spaCy model
echo Downloading spaCy English model...
python -m spacy download en_core_web_sm

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file with your configuration
)

echo.
echo === Setup Complete ===
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Start PostgreSQL and Redis servers
echo 3. Create database: createdb resume_analyzer
echo 4. Run migrations: flask db upgrade
echo 5. Start the application: python run.py
echo.
pause
