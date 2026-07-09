@echo off
echo ===================================================
echo  CAI DAT CSB BACKEND SERVICE (khong can NSSM)
echo  Chay voi quyen Administrator tren SERVER
echo ===================================================
echo.

set BACKEND_DIR=C:\WHO\csbwhoiswho\backend

echo [1/3] Xoa task cu neu co...
schtasks /delete /tn "CSBBackend" /f >nul 2>&1

echo [2/3] Tao Scheduled Task tu dong chay khi Windows khoi dong...
schtasks /create /tn "CSBBackend" ^
    /tr "\"%BACKEND_DIR%\run_backend_service.bat\"" ^
    /sc ONSTART ^
    /ru SYSTEM ^
    /rl HIGHEST ^
    /sd 01/01/2024 ^
    /f
if errorlevel 1 (
    echo LOI: Khong tao duoc Scheduled Task - can quyen Administrator
    pause
    exit /b 1
)
echo    OK - Da tao Scheduled Task "CSBBackend"

echo.
echo [3/3] Chay backend ngay bay gio...
cd /d "%BACKEND_DIR%"
start "CSB Backend" /MIN cmd /c "venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 7000"
timeout /t 4 /nobreak >nul

curl -s http://localhost:7000/ 2>nul | findstr "CSB" >nul
if errorlevel 1 (
    echo    CANH BAO: Backend chua phan hoi. Thu kiem tra thu cong.
) else (
    echo    OK - Backend dang chay tai http://localhost:7000
)

echo.
echo ===================================================
echo  XONG! Backend se tu dong khoi dong cung Windows.
echo ===================================================
echo.
pause
