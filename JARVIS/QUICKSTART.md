# Inicio Rápido de J.A.R.V.I.S.

## Paso 1: Verificar Ollama

Asegúrate de tener Ollama instalado y corriendo:

```powershell
ollama --version
```

Si no está instalado, descarga desde: https://ollama.com

## Paso 2: Descargar Modelos

Ejecuta este script para descargar los modelos necesarios:

```powershell
.\scripts\download-models.ps1
```

Esto descargará:
- `qwen2.5-coder:3b-instruct-q4_K_M` (~2GB) - Para código
- `llama3.2:3b-instruct-q4_K_M` (~2GB) - Para conversación general

## Paso 3: Instalar Dependencias

```powershell
.\scripts\setup.bat
```

## Paso 4: Iniciar J.A.R.V.I.S.

```powershell
.\scripts\start.bat
```

Se abrirán dos ventanas:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000

## Paso 5: ¡Usa tu Asistente!

Abre http://localhost:3000 en tu navegador y comienza a chatear.

---

**Nota**: La primera vez que envíes un mensaje, puede tardar unos segundos mientras el modelo carga en memoria. Es normal.
