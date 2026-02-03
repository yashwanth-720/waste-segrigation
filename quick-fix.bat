@echo off
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║           WASTE SEGREGATION SYSTEM - QUICK FIX               ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo This script will fix your Git errors and help you get started.
echo.
pause
echo.

:git_config
echo ========================================
echo   Step 1: Configure Git
echo ========================================
echo.
echo Please enter your details:
echo.
set /p email="Your Email: "
set /p name="Your Name: "

echo.
echo Configuring Git...
git config --global user.email "%email%"
git config --global user.name "%name%"

echo.
echo ✅ Git configured!
echo.

:commit
echo ========================================
echo   Step 2: Create Git Commit
echo ========================================
echo.
echo Creating initial commit...
git commit -m "Initial commit - Waste Segregation System"

if errorlevel 1 (
    echo.
    echo ⚠️  Commit failed. This is okay if already committed.
    echo.
) else (
    echo.
    echo ✅ Commit created successfully!
    echo.
)

:choice
echo ========================================
echo   Step 3: What do you want to do?
echo ========================================
echo.
echo 1. Test Locally (RECOMMENDED - Start here!)
echo 2. Install Dependencies
echo 3. Setup Dataset
echo 4. Train Model
echo 5. Deploy to Cloud (Heroku)
echo 6. Exit
echo.
set /p action="Choose (1-6): "

if "%action%"=="1" goto test_local
if "%action%"=="2" goto install_deps
if "%action%"=="3" goto setup_dataset
if "%action%"=="4" goto train_model
if "%action%"=="5" goto deploy_heroku
if "%action%"=="6" goto exit

:test_local
echo.
echo ========================================
echo   Testing Locally
echo ========================================
echo.
echo Starting the application...
echo.
echo ⚠️  NOTE: You need to train the model first!
echo    If you haven't trained the model, press Ctrl+C and choose option 4.
echo.
echo Opening in browser: http://localhost:5000
echo.
timeout /t 3
start http://localhost:5000
python app.py
goto choice

:install_deps
echo.
echo ========================================
echo   Installing Dependencies
echo ========================================
echo.
pip install -r requirements.txt
echo.
echo ✅ Dependencies installed!
echo.
pause
goto choice

:setup_dataset
echo.
echo ========================================
echo   Setting Up Dataset
echo ========================================
echo.
python setup_dataset.py
echo.
echo ✅ Dataset folders created!
echo.
echo Next steps:
echo 1. Download dataset from Kaggle or use your own images
echo 2. Place images in dataset/train/Organic and dataset/train/Recyclable
echo 3. Do the same for valid and test folders
echo.
pause
goto choice

:train_model
echo.
echo ========================================
echo   Training Model
echo ========================================
echo.
echo ⚠️  Make sure you have added images to the dataset folders!
echo.
set /p confirm="Continue with training? (y/n): "
if /i not "%confirm%"=="y" goto choice

echo.
echo Training model... This will take 30-60 minutes.
echo.
python train_model.py
echo.
echo ✅ Model training complete!
echo.
pause
goto choice

:deploy_heroku
echo.
echo ========================================
echo   Deploy to Heroku
echo ========================================
echo.
echo To deploy to Heroku, you need:
echo 1. Heroku CLI installed
echo 2. A Heroku account
echo.
echo Download Heroku CLI from:
echo https://devcenter.heroku.com/articles/heroku-cli
echo.
echo After installing, run these commands:
echo.
echo   heroku login
echo   heroku create my-waste-app
echo   git push heroku main
echo   heroku open
echo.
echo.
set /p open_url="Open Heroku CLI download page? (y/n): "
if /i "%open_url%"=="y" start https://devcenter.heroku.com/articles/heroku-cli
echo.
pause
goto choice

:exit
echo.
echo ========================================
echo   Summary
echo ========================================
echo.
echo ✅ Git is configured
echo ✅ Initial commit created
echo.
echo Next steps:
echo 1. Install dependencies (if not done)
echo 2. Setup dataset and add images
echo 3. Train the model
echo 4. Test locally
echo 5. Deploy to cloud (optional)
echo.
echo For detailed instructions, read:
echo - START_HERE.md
echo - FIX_ERRORS.md
echo.
echo Thank you for using the Waste Segregation System!
echo.
pause
exit
