@echo off
REM Script to keep uvicorn backend running persistently
REM Run this once from cmd.exe as Administrator or via Task Scheduler
REM It will automatically restart if uvicorn crashes

title CSB WHO Backend

:CHECK_PORT
netstat -ano | findstr ":7000 " | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo [%DATE% %TIME%] Port 7000 not listening, starting backend...
    goto START
) else (
    echo [%DATE% %TIME%] Backend already running on port 7000
    timeout /t 30 /nobreak >nul
    goto CHECK_PORT
)

:START
cd /d C:\WHO\csbwhoiswho\backend
echo [%DATE% %TIME%] Starting uvicorn on port 7000...
C:\WHO\csbwhoiswho\backend\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 7000 --log-level info
echo [%DATE% %TIME%] Backend stopped (exit code %ERRORLEVEL%), restarting in 3s...
timeout /t 3 /nobreak >nul
goto START
