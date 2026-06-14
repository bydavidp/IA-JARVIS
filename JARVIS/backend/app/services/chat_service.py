from typing import AsyncGenerator, Optional
from ..core.ollama import ollama_client


# Prompts de sistema para diferentes modos
SYSTEM_PROMPTS = {
    "general": """Eres J.A.R.V.I.S., un asistente de IA personal para un estudiante de Ingeniería de Sistemas.
- Responde de forma clara, concisa y educativa
- Explica conceptos técnicos de manera accesible
- Usa ejemplos prácticos cuando sea útil
- No hagas el trabajo por el usuario, guíalo para que aprenda
- Sé amigable pero profesional""",

    "code": """Eres un experto en programación que ayuda a estudiantes de Ingeniería de Sistemas.
- Analiza el código y explica qué hace
- Señala errores potenciales o mejoras
- Usa buenas prácticas y patrones de diseño
- Explica el "por qué" detrás de las recomendaciones
- Lenguajes principales: Python, Java, C++""",

    "math": """Eres un tutor de matemáticas para Ingeniería de Sistemas.
- Explica conceptos paso a paso
- Usa notación clara y ejemplos numéricos
- Relaciona la teoría con aplicaciones prácticas en computación
- Verifica que el usuario entienda cada paso""",

    "networks": """Eres un experto en redes y sistemas para Ingeniería de Sistemas.
- Explica protocolos, arquitecturas y configuraciones
- Usa ejemplos de escenarios reales
- Ayuda a diagnosticar problemas de red
- Explica conceptos como TCP/IP, DNS, HTTP, firewall, etc."""
}


class ChatService:
    """Servicio principal de chat con soporte para diferentes modos."""

    async def chat(
        self,
        message: str,
        mode: str = "general",
        context: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Procesa un mensaje de chat y genera respuesta streaming.

        Args:
            message: Mensaje del usuario
            mode: Modo de operación (general, code, math, networks)
            context: Contexto adicional (apuntes relevantes, historial, etc.)
        """
        system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["general"])

        # Agregar contexto si existe
        if context:
            system_prompt += f"\n\nContexto relevante:\n{context}"

        use_coder = mode == "code"

        async for token in ollama_client.chat(
            message=message,
            system_prompt=system_prompt,
            use_coder_model=use_coder,
            stream=True
        ):
            yield token

    async def analyze_code(self, code: str, language: str = "python") -> AsyncGenerator[str, None]:
        """
        Analiza código y proporciona explicaciones y mejoras.

        Args:
            code: Código a analizar
            language: Lenguaje de programación
        """
        prompt = f"""Analiza el siguiente código en {language}:

```{language}
{code}
```

Proporciona:
1. ¿Qué hace el código?
2. ¿Hay errores o problemas potenciales?
3. ¿Qué mejoras sugerirías?
4. Explica cualquier concepto importante que aparezca."""

        async for token in ollama_client.chat(
            message=prompt,
            system_prompt=SYSTEM_PROMPTS["code"],
            use_coder_model=True,
            stream=True
        ):
            yield token


chat_service = ChatService()
