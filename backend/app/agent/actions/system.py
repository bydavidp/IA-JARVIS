"""Acciones del sistema: volumen, ayuda, estado."""

import subprocess
import platform

from ..models import IntentResult, ActionResult
from ..config import ALLOWED_ACTIONS
from .base import BaseAction


class SystemActions(BaseAction):
    """Acciones de sistema con límites de seguridad."""

    async def execute(self, intent: IntentResult) -> ActionResult:
        action_map = {
            "volume_up": self._volume_up,
            "volume_down": self._volume_down,
            "help": self._help,
            "status": self._status,
        }
        handler = action_map.get(intent.intent.value)
        if not handler:
            return ActionResult(
                success=False,
                message="No reconozco esa acción del sistema.",
            )
        return await handler(intent)

    async def _volume_up(self, intent: IntentResult) -> ActionResult:
        if platform.system() == "Windows":
            try:
                subprocess.run(
                    [
                        "powershell",
                        "-c",
                        "(New-Object -ComObject WScript.Shell).SendKeys([char]175)",
                    ],
                    capture_output=True,
                    timeout=5,
                )
                return ActionResult(
                    success=True,
                    message="Subiendo el volumen un poco.",
                    data={"action": "volume_up"},
                )
            except Exception as e:
                return ActionResult(
                    success=False,
                    message=f"No pude ajustar el volumen: {e}",
                )
        return ActionResult(
            success=False,
            message="El control de volumen solo está disponible en Windows.",
        )

    async def _volume_down(self, intent: IntentResult) -> ActionResult:
        if platform.system() == "Windows":
            try:
                subprocess.run(
                    [
                        "powershell",
                        "-c",
                        "(New-Object -ComObject WScript.Shell).SendKeys([char]174)",
                    ],
                    capture_output=True,
                    timeout=5,
                )
                return ActionResult(
                    success=True,
                    message="Bajando el volumen un poco.",
                    data={"action": "volume_down"},
                )
            except Exception as e:
                return ActionResult(
                    success=False,
                    message=f"No pude ajustar el volumen: {e}",
                )
        return ActionResult(
            success=False,
            message="El control de volumen solo está disponible en Windows.",
        )

    async def _help(self, intent: IntentResult) -> ActionResult:
        lines = ["**Comandos disponibles:**\n"]
        for action, desc in ALLOWED_ACTIONS.items():
            lines.append(f"- **{action}**: {desc}")
        lines.extend([
            "",
            "**Ejemplos:**",
            "- \"Abre Spotify\"",
            "- \"Pon música relajante\"",
            "- \"Sube el volumen\"",
            "- \"Qué puedes hacer\"",
            "- \"Pausa la música\"",
        ])
        return ActionResult(
            success=True,
            message="\n".join(lines),
            data={"type": "help"},
        )

    async def _status(self, intent: IntentResult) -> ActionResult:
        return ActionResult(
            success=True,
            message=(
                "J.A.R.V.I.S. en línea. "
                "Sistema: operativo. "
                "Esperando instrucciones."
            ),
            data={
                "status": "online",
                "mode": "multimodal",
                "platform": platform.system(),
            },
        )
