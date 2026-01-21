@echo off
echo Starting Backend Server...
start cmd /k "python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"
echo Backend Server started in a new window.
echo.
echo Starting Frontend Server...
start cmd /k "cd frontend && npm run dev"
echo Frontend Server started in a new window.
echo.
echo System started successfully! Access it at http://localhost:5173
pause