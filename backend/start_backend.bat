@echo off
cd /d %~dp0
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 7000 --log-level info
pause