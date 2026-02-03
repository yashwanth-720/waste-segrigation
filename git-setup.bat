@echo off
echo ========================================
echo   Git Setup and Deployment Helper
echo ========================================
echo.

echo Step 1: Configuring Git...
echo.
set /p email="Enter your email: "
set /p name="Enter your name: "

git config --global user.email "%email%"
git config --global user.name "%name%"

echo.
echo ✅ Git configured successfully!
echo.

echo Step 2: Creating initial commit...
git add .
git commit -m "Initial commit - Waste Segregation System"

echo.
echo ✅ Initial commit created!
echo.

echo ========================================
echo   Deployment Options
echo ========================================
echo.
echo Choose your deployment method:
echo.
echo 1. Local Testing (Recommended First)
echo 2. Heroku (Cloud Deployment)
echo 3. Docker (Containerized)
echo 4. Skip Deployment
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto local
if "%choice%"=="2" goto heroku
if "%choice%"=="3" goto docker
if "%choice%"=="4" goto end

:local
echo.
echo ========================================
echo   Local Testing
echo ========================================
echo.
echo Starting local server...
echo Open your browser to: http://localhost:5000
echo.
python app.py
goto end

:heroku
echo.
echo ========================================
echo   Heroku Deployment
echo ========================================
echo.
echo First, you need to install Heroku CLI:
echo Download from: https://devcenter.heroku.com/articles/heroku-cli
echo.
echo After installing Heroku CLI, run these commands:
echo.
echo   heroku login
echo   heroku create your-app-name
echo   git push heroku main
echo   heroku open
echo.
pause
goto end

:docker
echo.
echo ========================================
echo   Docker Deployment
echo ========================================
echo.
echo Make sure Docker is installed, then run:
echo.
echo   docker build -t waste-app .
echo   docker run -p 5000:5000 waste-app
echo.
pause
goto end

:end
echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
pause
