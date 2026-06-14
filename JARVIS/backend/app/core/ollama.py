import httpx
from typing import AsyncGenerator, Optional
from .config import get_settings


class OllamaClient:
    """Cliente asíncrono para interactuar con Ollama."""

    def __init__(self):
        settings = get_settings()
        self.host = settings.ollama_host
        self.model_coder = settings.ollama_model_coder
        self.model_general = settings.ollama_model_general
        self.timeout = 120.0  # Segundos para respuestas largas

    async def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        use_coder_model: bool = False,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Envía un mensaje a Ollama y genera la respuesta stream.

        Args:
            message: Mensaje del usuario
            system_prompt: Prompt de sistema para contexto
            use_coder_model: Si True usa el modelo de código, si no el general
            stream: Si True, genera tokens uno a uno
        """
        model = self.model_coder if use_coder_model else self.model_general

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
            }
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.host}/api/chat",
                json=payload
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"Ollama error: {response.status_code} - {error_text.decode()}")

                async for line in response.aiter_lines():
                    if line:
                        import json
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue

    async def generate_embedding(self, text: str) -> list[float]:
        """Genera embedding para un texto usando el modelo de embeddings."""
        settings = get_settings()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.host}/api/embeddings",
                json={
                    "model": settings.embedding_model,
                    "prompt": text
                }
            )
            if response.status_code == 200:
                return response.json().get("embedding", [])
            return []

    async def health_check(self) -> bool:
        """Verifica si Ollama está disponible."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.host}/api/tags")
                return response.status_code == 200
        except Exception:
            return False


# Instancia global para reutilizar
ollama_client = OllamaClient()
