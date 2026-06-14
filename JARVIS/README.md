# J.A.R.V.I.S. - Asistente IA Personal Futurista

Asistente de IA personal para estudiantes de Ingeniería de Sistemas. Ejecución 100% local usando Ollama, con interfaz visual animada, síntesis de voz y reconocimiento de habla.

## 🚀 Características Principales

- **Rostro Visual Animado**: Interfaz HUD futurista que reacciona en tiempo real (Escuchando, Procesando, Hablando, Inactivo).
- **Interacción por Voz**: Reconocimiento de habla (STT) integrado para comandos manos libres.
- **Síntesis de Voz (TTS)**: JARVIS responde con una voz grave y seria configurada para sonar profesional.
- **Cerebro Local**: Conexión con Ollama para procesamiento de lenguaje natural sin depender de la nube.

## 📋 Requisitos

- **Python 3.11+**
- **Node.js 18+**
- **Ollama** instalado y corriendo en Windows.
- **Navegador Moderno** (Chrome o Edge recomendados para soporte completo de Web Speech API).

## 🛠️ Instalación

### 1. Descargar modelos de Ollama
Abre PowerShell y ejecuta:
```powershell
ollama pull qwen2.5-coder:3b-instruct-q4_K_M
ollama pull llama3.2:3b-instruct-q4_K_M
```

### 2. Configurar el proyecto
Ejecuta el script de setup para instalar dependencias de Python y Node.js:
```powershell
.\scripts\setup.bat
```

## 🕹️ Uso

### Iniciar J.A.R.V.I.S.
Ejecuta el script de inicio:
```powershell
.\scripts\start.bat
```
Esto abrirá el Backend (FastAPI) y el Frontend (React + Vite).

### Acceder a la interfaz
Abre tu navegador en: **http://localhost:3000**

### Interacción
- **Teclado**: Escribe tu mensaje en el chat y presiona Enter.
- **Voz**: Haz clic en el icono del micrófono 🎤, habla, y JARVIS procesará tu solicitud automáticamente.

## 🎭 Modos de Chat
| Modo | Descripción |
|------|-------------|
| 💬 General | Conversación y conceptos generales |
| 💻 Código | Análisis de Python, Java, C++ |
| 📐 Matemáticas | Problemas y conceptos matemáticos |
| 🌐 Redes | Protocolos, TCP/IP, sistemas |

## 🏗️ Estructura del Proyecto
```
jarvis/
├── backend/           # API FastAPI (Python)
│   ├── app/
│   │   ├── api/      # Endpoints REST
│   │   ├── core/     # Configuración, cliente Ollama
│   │   ├── db/       # Base de datos SQLite
│   │   ├── models/   # Modelos SQLAlchemy
│   │   └── services/ # Lógica de negocio
│   └── venv/         # Entorno virtual
├── frontend/          # Interfaz React + Tailwind
│   └── src/
│       ├── components/ # UI (JarvisFace, Chat)
│       ├── services/    # TTS y STT (VoiceService, SpeechService)
│       └── App.tsx      # Orquestación principal
└── scripts/           # Automatización de inicio
```

## ⚙️ Tecnologías
- **Backend**: FastAPI, SQLAlchemy, HTTPX
- **Frontend**: React 18, TypeScript, TailwindCSS
- **Voz**: Web Speech API (Synthesis & Recognition)
- **IA**: Ollama (qwen2.5-coder, llama3.2)
- **Base de Datos**: SQLite
