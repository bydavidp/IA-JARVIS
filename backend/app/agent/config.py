"""Listas blancas de acciones y aplicaciones permitidas."""

from typing import TypedDict


class AppEntry(TypedDict):
    path: str
    name: str


# Acciones permitidas (whitelist central)
ALLOWED_ACTIONS: dict[str, str] = {
    "chat": "Conversación general con el asistente",
    "open_app": "Abrir aplicaciones permitidas",
    "play_music": "Reproducir música o playlist",
    "pause_music": "Pausar la reproducción actual",
    "resume_music": "Reanudar la reproducción",
    "stop_music": "Detener la reproducción",
    "volume_up": "Subir el volumen (máximo 80%)",
    "volume_down": "Bajar el volumen (mínimo 10%)",
    "help": "Mostrar lista de comandos y capacidades",
    "status": "Consultar estado interno del asistente",
}

# Aplicaciones permitidas para abrir (alias → ejecutable)
ALLOWED_APPS: dict[str, AppEntry] = {
    "navegador": {"path": "msedge.exe", "name": "Microsoft Edge"},
    "chrome": {"path": "chrome.exe", "name": "Google Chrome"},
    "edge": {"path": "msedge.exe", "name": "Microsoft Edge"},
    "spotify": {"path": "spotify.exe", "name": "Spotify"},
    "vscode": {"path": "Code.exe", "name": "Visual Studio Code"},
    "calculadora": {"path": "calc.exe", "name": "Calculadora"},
    "notepad": {"path": "notepad.exe", "name": "Bloc de notas"},
    "bloc de notas": {"path": "notepad.exe", "name": "Bloc de notas"},
    "explorador": {"path": "explorer.exe", "name": "Explorador de archivos"},
    "explorador de archivos": {"path": "explorer.exe", "name": "Explorador de archivos"},
}

ACCIONES_SENSIBLES: set[str] = {
    "open_app",
}

ACCIONES_SIN_CONFIRMAR: set[str] = {
    "chat",
    "help",
    "status",
    "pause_music",
    "resume_music",
    "stop_music",
    "volume_up",
    "volume_down",
}

# Acciones denegadas explícitamente (nunca ejecutar)
ACCIONES_DENEGADAS: list[str] = [
    "borrar", "eliminar", "mover", "renombrar", "editar_archivo",
    "ejecutar_script", "cambiar_config_sistema", "formatear",
    "apagar", "reiniciar", "comando_arbitrario",
]

# Patrones de seguridad para detectar intentos maliciosos
PATRONES_RECHAZO: list[str] = [
    "borra", "elimina", "suprime",
    "mueve", "traslada", "renombra",
    "ejecuta", "corre", "lanza",
    "formatea", "formatear",
    "apaga", "reinicia",
    "modifica.*archivo", "edita.*archivo",
    "rm ", "del ", "format ",
]
