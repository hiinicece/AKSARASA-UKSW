@echo off
echo ================================================
echo Starting Museum AI Backend Server
echo ================================================
echo.
echo Backend API will run on: http://localhost:5000
echo Frontend will run on: http://localhost:8000
echo.
echo Press Ctrl+C to stop the servers
echo ================================================
echo.

REM Check if .env exists, if not create it
cd ..\backend
if not exist .env (
    echo GEMINI_API_KEY=your_api_key_here > .env
    echo.
    echo [!] File .env created. Please edit it and add your API key.
    echo     Get free API key from: https://makersuite.google.com/app/apikey
    echo.
)

start "Backend Server" cmd /k "python server.py"
timeout /t 3 /nobreak > nul

REM
cd ..\frontend
start "Frontend Server" cmd /k "python -m http.server 8000"

echo.
echo Servers started!
echo.
echo Open your browser and go to:
echo http://localhost:8000
echo.
pause
