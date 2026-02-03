@echo off
echo ========================================
echo   AI Waste Segregation System
echo   Quick Start Script
echo ========================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo To train the model:
echo   python train_model.py
echo.
echo To run the web application:
echo   python app.py
echo.
echo Then open: http://localhost:5000
echo ========================================
echo.

set /p choice="Do you want to start the web application now? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo Starting web application...
    python app.py
) else (
    echo.
    echo You can start the application later with: python app.py
)

pause
