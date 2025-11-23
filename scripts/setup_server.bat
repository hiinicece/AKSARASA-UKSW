@echo off
echo ================================================
echo Museum AI Backend - Setup Script
echo ================================================
echo.

echo [1/3] Installing Python packages...
pip install -r requirements.txt

echo.
echo [2/3] Checking .env file...
if not exist .env (
    echo Creating .env file from example...
    copy .env.example .env
    echo.
    echo ⚠ IMPORTANT: Please edit .env file and add your GEMINI_API_KEY
    echo Get free API key from: https://makersuite.google.com/app/apikey
    echo.
    pause
) else (
    echo .env file already exists
)

echo.
echo [3/3] Setup complete!
echo.
echo ================================================
echo To start the server, run: start_server.bat
echo ================================================
pause
