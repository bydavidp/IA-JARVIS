"""
J.A.R.V.I.S. Backend - Asistente IA Personal para Ingeniería de Sistemas

API REST construida con FastAPI que se conecta a Ollama local.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import chat, memory
from ..db.database import engine, Base
from ..core.config import get_settings

# Crear tablas de base de datos
Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(
    title="J.A.R.V.I.S.",
    description="Asistente IA Personal para Ingeniería de Sistemas",
    version="0.1.0"
)

# Configurar CORS para permitir conexión desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar el dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint de health check."""
    return {
        "name": "J.A.R.V.I.S.",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Verifica el estado del backend y conexión con Ollama."""
    from ..core.ollama import ollama_client

    ollama_status = await ollama_client.health_check()

    return {
        "backend": "healthy",
        "ollama": "connected" if ollama_status else "disconnected",
        "database": "connected"
    }


# Registrar rutas
app.include_router(chat.router)
app.include_router(memory.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.api.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )
