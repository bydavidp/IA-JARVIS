@echo off
title JARVIS Voice Assistant - Local Premium Edition
echo.
echo ============================================================
echo    J.A.R.V.I.S. Voice Assistant - Local Premium Edition
echo    Voice-Activated AI Assistant for Local Use Only
echo ============================================================
echo.

REM Check if virtual environment exists, if not create and use it
if not exist "backend\venv\Scripts\activate" (
    echo Creating virtual environment...
    python -m venv backend\venv
)

REM Activate virtual environment
call backend\venv\Scripts\activate

REM Install voice requirements if not already installed
echo Checking and installing voice requirements...
pip install -r requirements_voice.txt

REM Run system check
echo.
echo Running system check...
python utils\system_check.py
if errorlevel 1 (
    echo.
    echo System check failed. Please resolve issues above.
    echo.
    pause
    exit /b 1
)

REM Check if voice is enrolled
if not exist "data\voice_print.pkl" (
    echo.
    echo Voice not enrolled. Please enroll your voice first.
    echo.
    python enroll_voice.py
    if errorlevel 1 (
        echo.
        echo Voice enrollment failed or was cancelled.
        echo.
        pause
        exit /b 1
    )
)

REM Start the voice assistant
echo.
echo Starting JARVIS Voice Assistant...
echo Say "Jarvis" to activate the assistant.
echo Press Ctrl+C to stop.
echo.
python main.py

REM Keep window open if exited with error
if errorlevel 1 (
    echo.
    echo Voice assistant exited with error.
    pause
)