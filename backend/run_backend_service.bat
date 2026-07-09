@echo off
:RESTART
echo [%DATE% %TIME%] Starting CSB Backend on port 7000...
cd /d C:\WHO\csbwhoiswho\backend
C:\WHO\csbwhoiswho\backend\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 7000
echo [%DATE% %TIME%] Backend exited (code %ERRORLEVEL%). Restarting in 5 seconds...
timeout /t 5 /nobreak
goto RESTART
