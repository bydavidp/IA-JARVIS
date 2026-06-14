import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# Directorio raíz del proyecto (backend/app/core/ -> ../../..)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    """Configuración del backend cargada desde variables de entorno."""

    # Ollama
    ollama_host: str = "http://127.0.0.1:11434"
    ollama_model_coder: str = "qwen2.5-coder:3b-instruct-q4_K_M"
    ollama_model_general: str = "llama3.2:3b-instruct-q4_K_M"

    # Base de datos
    database_url: str = f"sqlite:///{ROOT_DIR / 'data' / 'jarvis.db'}"

    # Servidor
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = str(ROOT_DIR / ".env")
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Retorna configuración cached para evitar recargar constantemente."""
    return Settings()
