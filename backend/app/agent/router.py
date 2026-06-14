"""Router de intenciones: clasifica mensajes y enruta a acciones."""

import re
import json
from typing import AsyncGenerator

from ..core.ollama import ollama_client
from .models import IntentType, IntentResult, ActionResult
from .permissions import validar_intencion
from .config import ALLOWED_APPS
from .actions.app_launcher import AppLauncher
from .actions.music_player import MusicPlayer
from .actions.system import SystemActions

# ── Patrones rápidos (sin LLM) para comandos comunes ──

PATRONES_ACCION: list[tuple[re.Pattern, str, callable]] = [
    # open_app
    (re.compile(r"^(abre|abrir|inicia|iniciar|lanza|lanzar|ejecuta|ejecutar|abrime)\s+(.+)", re.I), "open_app",
     lambda m: {"app_name": m.group(2).strip().lower()}),
    (re.compile(r"^(abreme|abrirme)\s+(.+)", re.I), "open_app",
     lambda m: {"app_name": m.group(2).strip().lower()}),
    # play_music
    (re.compile(r"^(pon|poner|reproduce|reproducir|ponme|coloca|busca)\s+(música|musica|m[uú]sica\s+\w+)\b(.+)", re.I), "play_music",
     lambda m: {"query": (m.group(2) + " " + m.group(3)).strip()}),
    (re.compile(r"^(pon|poner|reproduce|reproducir|ponme|coloca|busca)\s+(.+)", re.I), "play_music",
     lambda m: {"query": m.group(2).strip()}),
    (re.compile(r"^(quiero\s+)?(escuchar|o[ií]r)\s+(.+)", re.I), "play_music",
     lambda m: {"query": m.group(3).strip()}),
    # pause / resume / stop
    (re.compile(r"^(pausa|det[eé]n|para|detener|pausar)\s+(la\s+)?(m[uú]sica|música|canci[oó]n|reproducci[oó]n)", re.I), "pause_music",
     lambda m: {}),
    (re.compile(r"^((contin[uú]a|sigue|reanuda|reanudar)\s+(la\s+)?(m[uú]sica|música|canci[oó]n|reproducci[oó]n))", re.I), "resume_music",
     lambda m: {}),
    (re.compile(r"^(para|det[eé]n|detener|para\s+todo)\s+(la\s+)?(m[uú]sica|música|canci[oó]n)", re.I), "stop_music",
     lambda m: {}),
    # volume
    (re.compile(r"^(sube|sub[ií]|aumenta|aumentar)\s+(el\s+)?(volumen|audio)", re.I), "volume_up", lambda m: {}),
    (re.compile(r"^(baja|bajar|reduce|reducir|disminuye)\s+(el\s+)?(volumen|audio)", re.I), "volume_down", lambda m: {}),
    (re.compile(r"^volumen\s+(m[aá]s|arriba|sube|alto)", re.I), "volume_up", lambda m: {}),
    (re.compile(r"^volumen\s+(menos|abajo|baja|bajo)", re.I), "volume_down", lambda m: {}),
    # help
    (re.compile(r"^(qu[eé] puedes hacer|qu[eé] haces|ayuda|help|comandos|capacidades|qu[eé] sabes hacer)", re.I), "help", lambda m: {}),
    # status
    (re.compile(r"^(c[oó]mo est[aá]s|estado|status|c[oó]mo vas|qu[eé] tal)", re.I), "status", lambda m: {}),
    # reject
    (re.compile(r"(borra|elimina|suprime|mueve|renombra|formatea|apaga).*(archivos|documentos|carpetas|fotos)", re.I), "reject", lambda m: {}),
]

PATRONES_CHAT = [
    re.compile(r"^(qu[eé] es|qu[eé] son|qu[eé] significa|define|expl[ií]came|c[oó]mo funciona|dime|cu[aá]l es|qui[eé]n es|cu[aá]ndo|d[oó]nde|por qu[eé])\b", re.I),
]


class AgentRouter:
    """Clasifica la intención del usuario y enruta a la acción apropiada."""

    def __init__(self):
        self._actions: dict[str, object] = {
            "open_app": AppLauncher(),
            "play_music": MusicPlayer(),
            "pause_music": MusicPlayer(),
            "resume_music": MusicPlayer(),
            "stop_music": MusicPlayer(),
            "volume_up": SystemActions(),
            "volume_down": SystemActions(),
            "help": SystemActions(),
            "status": SystemActions(),
        }

    def _clasificar_por_patron(self, message: str) -> IntentResult | None:
        """Clasificación rápida por patrón — sin LLM."""
        msg = message.strip()

        for patron, intent_name, extractor in PATRONES_ACCION:
            m = patron.search(msg)
            if m:
                params = extractor(m)
                try:
                    intent = IntentType(intent_name)
                except ValueError:
                    continue
                return IntentResult(
                    intent=intent,
                    parameters=params,
                    confidence=0.9,
                    original_message=message,
                    explanation=f"Clasificado por patrón: {intent_name}",
                )

        for patron in PATRONES_CHAT:
            if patron.match(msg):
                return IntentResult(
                    intent=IntentType.CHAT,
                    parameters={},
                    confidence=0.85,
                    original_message=message,
                    explanation="Clasificado como chat por patrón de pregunta",
                )

        return None

    async def _clasificar_con_llm(self, message: str) -> IntentResult:
        """Clasificación usando Ollama (fallback cuando el patrón no alcanza)."""
        SYSTEM_PROMPT = """\
Eres un clasificador de intenciones para J.A.R.V.I.S.

Responde SOLO con JSON:
{"intent": "chat"|"open_app"|"play_music"|"pause_music"|"resume_music"|"stop_music"|"volume_up"|"volume_down"|"help"|"status"|"reject"|"unknown", "parameters": {}, "confidence": 0.0-1.0}

- open_app → {"app_name": "..."}
- play_music → {"query": "..."}
- reject para: borrar, eliminar, mover, renombrar, ejecutar scripts, formatear, apagar"""
        try:
            tokens = []
            async for token in ollama_client.chat(
                message=message,
                system_prompt=SYSTEM_PROMPT,
                use_coder_model=True,
                stream=True,
            ):
                tokens.append(token)

            texto = "".join(tokens).strip()
            texto = re.sub(r"^```json\s*", "", texto)
            texto = re.sub(r"\s*```$", "", texto)
            texto = texto.strip()

            data = json.loads(texto)
            intent_str = data.get("intent", "unknown")
            try:
                intent = IntentType(intent_str)
            except ValueError:
                intent = IntentType.UNKNOWN

            return IntentResult(
                intent=intent,
                parameters=data.get("parameters", {}),
                confidence=data.get("confidence", 0.0),
                original_message=message,
                explanation=data.get("explanation", ""),
            )
        except Exception:
            return IntentResult(
                intent=IntentType.CHAT,
                parameters={},
                confidence=0.3,
                original_message=message,
                explanation="Fallback a chat por error de clasificación",
            )

    async def classify(self, message: str) -> IntentResult:
        """Intenta patrón primero; si no, usa LLM."""
        resultado = self._clasificar_por_patron(message)
        if resultado is not None:
            return resultado
        return await self._clasificar_con_llm(message)

    async def route(
        self, message: str, mode: str = "general"
    ) -> AsyncGenerator[str, None]:
        """Clasifica, valida permisos y ejecuta la acción."""
        intent = await self.classify(message)

        if intent.intent == IntentType.REJECT:
            yield (
                "No puedo realizar esa acción. Por seguridad, no borro, "
                "muevo, renombro ni ejecuto archivos o comandos en tu sistema."
            )
            return

        validation = validar_intencion(intent)
        if not validation.success:
            yield validation.message
            return

        if intent.intent.value in self._actions:
            handler = self._actions[intent.intent.value]
            result = await handler.execute(intent)
            yield result.message
            return

        if intent.intent == IntentType.CHAT:
            yield "__CHAT_FALLBACK__"
            return

        yield (
            "No entendí bien lo que quieres. Puedes decirme 'qué puedes hacer' "
            "para ver mis capacidades."
        )


agent_router = AgentRouter()
