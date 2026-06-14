@echo off
title JARVIS Voice Assistant Cleanup
echo.
echo ============================================================
echo    J.A.R.V.I.S. Voice Assistant Cleanup
echo ============================================================
echo.

REM Stop any running processes
echo Stopping any running JARVIS processes...
taskkill /f /i python.exe >nul 2>&1

REM Ask about removing voice print
set /p remove_voice=Remove voice print data? (y/N):
if /i "%remove_voice%"=="y" (
    if exist "data\voice_print.pkl" (
        del "data\voice_print.pkl"
        echo Voice print removed.
    ) else (
        echo No voice print found.
    )
) else (
    echo Voice print preserved.
)

REM Ask about removing logs
set /p remove_logs=Remove log files? (y/N):
if /i "%remove_logs%"=="y" (
    if exist "logs\" (
        rmdir /s /q "logs\"
        mkdir "logs\"
        echo Logs cleared.
    ) else (
        echo No logs directory found.
    )
) else (
    echo Logs preserved.
)

REM Ask about removing virtual environment
set /p remove_venv=Remove virtual environment? (y/N):
if /i "%remove_venv%"=="y" (
    if exist "backend\venv\" (
        rmdir /s /q "backend\venv\"
        echo Virtual environment removed.
    ) else (
        echo No virtual environment found.
    )
) else (
    echo Virtual environment preserved.
)

echo.
echo Cleanup complete.
echo.
pause