@echo off
title CSB System Local Runner
echo ===================================================
echo Khởi động hệ thống CSB Who Is Who (Không dùng Docker)
echo ===================================================
echo.

echo [1/2] Đang khởi động Backend (FastAPI - Port 7000)...
start "CSB Backend" cmd /c "cd backend && (if exist venv\Scripts\activate call venv\Scripts\activate || echo Khong tim thay venv, dang chay truc tiep) && pip install -r requirements.txt && python run.py"

echo [2/2] Đang khởi động Frontend (Vite/React - Port 5173)...
start "CSB Frontend" cmd /c "cd frontend && npm install && npm run dev"

echo.
echo Cả 2 dịch vụ đang được khởi chạy trong 2 cửa sổ cmd riêng biệt!
echo.
echo - Frontend (Giao diện): http://localhost:5173
echo - Backend (API): http://localhost:7000
echo.
echo Để tắt hệ thống, vui lòng đóng 2 cửa sổ cmd màu đen vừa mở.
pause
