"""Control de reproducción musical encapsulado."""

import subprocess
import webbrowser
from urllib.parse import quote

from ..models import IntentResult, ActionResult
from ..config import ALLOWED_APPS
from .base import BaseAction


class MusicPlayer(BaseAction):
    """
    Adaptador de música. Soporta:
    - Abrir Spotify directamente
    - Buscar en YouTube Music / navegador
    """

    def __init__(self):
        self._is_playing = False
        self._current_query = ""

    async def execute(self, intent: IntentResult) -> ActionResult:
        action_map = {
            "play_music": self._play,
            "pause_music": self._pause,
            "resume_music": self._resume,
            "stop_music": self._stop,
        }
        handler = action_map.get(intent.intent.value)
        if not handler:
            return ActionResult(
                success=False,
                message="No reconozco esa acción musical.",
            )
        return await handler(intent)

    async def _play(self, intent: IntentResult) -> ActionResult:
        query = intent.parameters.get("query", "")

        # Intentar abrir Spotify primero
        spotify_entry = ALLOWED_APPS.get("spotify")
        if spotify_entry:
            try:
                resolved = subprocess.which(spotify_entry["path"])
                if resolved:
                    subprocess.Popen([resolved], shell=False)
                else:
                    subprocess.Popen([spotify_entry["path"]], shell=True)
            except Exception:
                pass

        # Si hay query, buscar en YouTube Music vía navegador
        if query:
            search_url = f"https://music.youtube.com/search?q={quote(query)}"
            webbrowser.open(search_url, new=2, autoraise=False)
            self._is_playing = True
            self._current_query = query
            return ActionResult(
                success=True,
                message=f"Buscando '{query}' en YouTube Music. " if query
                else "Abriendo Spotify.",
                data={"query": query, "service": "youtube_music"},
            )

        return ActionResult(
            success=True,
            message="Abriendo Spotify.",
            data={"service": "spotify"},
        )

    async def _pause(self, intent: IntentResult) -> ActionResult:
        self._is_playing = False
        return ActionResult(
            success=True,
            message="Pausando la música.",
            data={"action": "pause"},
        )

    async def _resume(self, intent: IntentResult) -> ActionResult:
        if not self._current_query:
            return ActionResult(
                success=True,
                message="No hay música que reanudar. ¿Quieres que reproduzca algo?",
            )
        self._is_playing = True
        search_url = f"https://music.youtube.com/search?q={quote(self._current_query)}"
        webbrowser.open(search_url, new=2, autoraise=False)
        return ActionResult(
            success=True,
            message=f"Reanudando búsqueda de '{self._current_query}'.",
            data={"query": self._current_query},
        )

    async def _stop(self, intent: IntentResult) -> ActionResult:
        self._is_playing = False
        self._current_query = ""
        return ActionResult(
            success=True,
            message="Deteniendo la reproducción.",
            data={"action": "stop"},
        )
