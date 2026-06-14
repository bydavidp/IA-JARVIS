@echo off
echo ========================================
echo   J.A.R.V.I.S. - Setup Inicial
echo ========================================
echo.

REM Crear entorno virtual de Python
echo [1/4] Creando entorno virtual de Python...
cd backend
python -m venv venv
call venv\Scripts\activate

REM Instalar dependencias de Python
echo [2/4] Instalando dependencias de Python...
pip install --upgrade pip
pip install -r requirements.txt

REM Crear directorio de datos
echo [3/3] Creando directorio de datos...
if not exist data mkdir data

echo.
echo ========================================
echo   Setup completado!
echo ========================================
echo.
echo Siguientes pasos:
echo 1. Asegurate de tener Ollama corriendo en Windows
echo 2. Descarga los modelos:
echo    ollama pull qwen2.5-coder:3b-instruct-q4_K_M
echo    ollama pull llama3.2:3b-instruct-q4_K_M
echo 3. Ejecuta start.bat para iniciar J.A.R.V.I.S.
echo.
