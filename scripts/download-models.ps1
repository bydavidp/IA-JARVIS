# Script para descargar modelos de Ollama para J.A.R.V.I.S.

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  J.A.R.V.I.S. - Descarga de Modelos" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Ollama está instalado
try {
    $ollamaVersion = ollama --version
    Write-Host "[OK] Ollama instalado: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Ollama no está instalado." -ForegroundColor Red
    Write-Host "Descarga Ollama desde: https://ollama.com" -ForegroundColor Yellow
    exit 1
}

# Verificar si Ollama está corriendo
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "[OK] Ollama está corriendo en localhost:11434" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Ollama no está corriendo." -ForegroundColor Red
    Write-Host "Ejecuta 'ollama serve' en una terminal primero." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Descargando modelos (esto puede tardar varios minutos)..." -ForegroundColor Cyan
Write-Host ""

# Modelo para código
Write-Host "[1/2] Descargando qwen2.5-coder:3b-instruct-q4_K_M..." -ForegroundColor Yellow
ollama pull qwen2.5-coder:3b-instruct-q4_K_M

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Modelo de código descargado!" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Error al descargar el modelo de código" -ForegroundColor Red
}

Write-Host ""

# Modelo general
Write-Host "[2/2] Descargando llama3.2:3b-instruct-q4_K_M..." -ForegroundColor Yellow
ollama pull llama3.2:3b-instruct-q4_K_M

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Modelo general descargado!" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Error al descargar el modelo general" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Modelos listos para usar!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ahora ejecuta: .\scripts\start.bat" -ForegroundColor Yellow
