@echo off
echo Starting CSB Who Is Who system...
echo.
echo Running docker-compose up -d --build
docker-compose up -d --build
echo.
echo The system is starting in the background.
echo You can access the frontend at: http://localhost:80
echo You can access the backend API at: http://localhost:8000
echo.
pause
