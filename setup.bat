@echo off
SETLOCAL

echo ============================================
echo   Clara AI Pipeline - Windows Setup
echo ============================================

REM Check Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Python not found. Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)
echo [OK] Python found.

REM Install dependencies
echo Installing Python dependencies...
pip install google-generativeai

echo.
echo ============================================
echo   SETUP COMPLETE
echo ============================================
echo.
echo NEXT STEP: Set your Gemini API key.
echo.
echo   1. Go to: https://aistudio.google.com/app/apikey
echo   2. Click "Create API Key" (it's FREE)
echo   3. Copy the key
echo   4. Run this command in your terminal:
echo.
echo      set GEMINI_API_KEY=your_key_here
echo.
echo Then run the pipeline:
echo      cd scripts
echo      python run_pipeline.py
echo.
pause
