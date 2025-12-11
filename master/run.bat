@echo off
REM Master Server Runner Script (Windows)

echo 🚀 Starting Master services...
echo    Backend: http://localhost:8000
echo    Frontend: http://localhost:3000
echo    (Press Ctrl+C to stop)
echo.

REM Check and install frontend dependencies
if not exist "frontend\node_modules" (
    echo 📦 Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

REM Check and install backend dependencies
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing backend dependencies...
    cd backend
    call pip install -r requirements.txt
    cd ..
)

REM Start backend
echo 📦 Starting backend server...
start "Master Backend" cmd /k "cd backend && python main.py"

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start frontend
echo 📦 Starting frontend dev server...
start "Master Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Services started in separate windows
echo    Close the windows or press Ctrl+C to stop

pause

