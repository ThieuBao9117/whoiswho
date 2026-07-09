@echo off
cd /d C:\WHO\csbwhoiswho\backend
C:\WHO\csbwhoiswho\backend\venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 7000
