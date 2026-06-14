@echo off
echo ========================================
echo   Iniciando J.A.R.V.I.S.
echo ========================================
echo.

REM Iniciar backend en una ventana
echo [Backend] Iniciando servidor FastAPI en puerto 8000...
start "J.A.R.V.I.S. Backend" cmd /k "cd /d %~dp0.. && backend\venv\Scripts\activate && python -m uvicorn app.api.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000"

echo.
echo ========================================
echo   J.A.R.V.I.S. está iniciando...
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Docs API: http://localhost:8000/docs
echo.
echo Presiona Ctrl+C en cada ventana para detener los servidores.
echo.
