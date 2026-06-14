"""Abre aplicaciones permitidas usando subprocess."""

import subprocess
import shutil

from ..models import IntentResult, ActionResult
from ..config import ALLOWED_APPS
from .base import BaseAction


class AppLauncher(BaseAction):
    """Abre aplicaciones del sistema desde la lista blanca."""

    async def execute(self, intent: IntentResult) -> ActionResult:
        app_name = intent.parameters.get("app_name", "").lower()
        app_entry = ALLOWED_APPS.get(app_name)

        if not app_entry:
            return ActionResult(
                success=False,
                message=f"'{app_name}' no está en mi lista de aplicaciones permitidas.",
            )

        executable = app_entry["path"]
        app_display = app_entry["name"]

        try:
            resolved = shutil.which(executable)
            if resolved:
                subprocess.Popen([resolved], shell=False)
            else:
                subprocess.Popen([executable], shell=True)

            return ActionResult(
                success=True,
                message=f"Abriendo {app_display}.",
                data={"app": app_name, "executable": executable},
            )
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"No pude abrir {app_display}: {e}",
                data={"error": str(e)},
            )
