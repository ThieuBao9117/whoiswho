@echo off
title CSB WHO Backend - Port 7000

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
echo [%DATE% %TIME%] Starting uvicorn...
C:\WHO\csbwhoiswho\backend\venv\Scripts\python.exe -m uvicorn app.main:app ^
    --host 127.0.0.1 ^
    --port 7000 ^
    --loop asyncio ^
    --http h11 ^
    --timeout-keep-alive 5 ^
    --log-level info
echo [%DATE% %TIME%] Backend stopped (exit %ERRORLEVEL%), restarting in 3s...
timeout /t 3 /nobreak >nul
goto START
