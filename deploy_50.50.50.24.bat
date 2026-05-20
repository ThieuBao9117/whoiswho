@echo off
echo ===================================================
echo CSB WHO IS WHO - DEPLOYMENT SCRIPT FOR 50.50.50.24
echo ===================================================

echo.
echo [1] THIET LAP BACKEND (PORT 7070)
echo.
cd backend
if not exist "venv\Scripts\python.exe" (
    echo Dang tao moi truong ao Python...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    echo Moi truong ao da san sang.
)

:: Create or update the backend service using NSSM (optional, if NSSM is installed)
echo.
echo Lenh de chay backend tren port 7070:
echo venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 7070
echo (Ban co the dua lenh nay vao Windows Service)
cd ..

echo.
echo [2] THIET LAP FRONTEND (PORT 5173)
echo.
echo Da build san thu muc frontend/dist
echo Lenh de chay frontend tren port 5173:
echo npx serve -s frontend\dist -l 5173
echo (Hoac su dung Nginx/IIS de tro vao thu muc frontend\dist)

echo.
echo DEPLOYMENT READY!
echo - API Base URL da duoc fix cung la: http://50.50.50.24:7070/api
echo - CORS da duoc mo cho: http://50.50.50.24:5173
echo.
pause
