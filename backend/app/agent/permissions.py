"""Validador central de permisos y seguridad."""

import re

from .config import (
    ALLOWED_ACTIONS,
    ALLOWED_APPS,
    ACCIONES_SENSIBLES,
    ACCIONES_SIN_CONFIRMAR,
    PATRONES_RECHAZO,
)
from .models import IntentType, IntentResult, ActionResult


def validar_intencion(result: IntentResult) -> ActionResult:
    """
    Valida una intención contra las listas blancas y devuelve
    un ActionResult indicando si procede o no.
    """
    # 1. Detectar intenciones maliciosas por patrón
    if _coincide_con_patron_rechazo(result.original_message):
        return ActionResult(
            success=False,
            message=(
                "No puedo realizar esa acción. "
                "Por seguridad, no borro, muevo, renombro ni ejecuto "
                "archivos o comandos en tu sistema."
            ),
            data={"reason": "rejected_by_pattern"},
        )

    # 2. Verificar que la acción esté en la lista blanca
    if result.intent.value not in ALLOWED_ACTIONS and result.intent != IntentType.UNKNOWN:
        return ActionResult(
            success=False,
            message=(
                f"La acción '{result.intent.value}' no está en mi lista de "
                f"capacidades permitidas. Usa 'ayuda' o 'qué puedes hacer' "
                f"para ver lo que puedo hacer."
            ),
            data={"reason": "action_not_allowed"},
        )

    # 3. Validar parámetros específicos por tipo de acción
    if result.intent == IntentType.OPEN_APP:
        app_name = result.parameters.get("app_name", "").lower()
        if app_name not in ALLOWED_APPS:
            apps_disponibles = ", ".join(sorted(ALLOWED_APPS.keys()))
            return ActionResult(
                success=False,
                message=(
                    f"'{app_name}' no está en mi lista de aplicaciones "
                    f"permitidas. Puedo abrir: {apps_disponibles}."
                ),
                data={"reason": "app_not_in_whitelist"},
            )

    # 4. Determinar si requiere confirmación
    requiere_confirmacion = (
        result.intent.value in ACCIONES_SENSIBLES
        and result.intent.value not in ACCIONES_SIN_CONFIRMAR
    )

    return ActionResult(
        success=True,
        message="Intención válida",
        requires_confirmation=requiere_confirmacion,
        data={"action": result.intent.value, "params": result.parameters},
    )


def pedir_confirmacion(result: IntentResult) -> str:
    """Genera mensaje de confirmación para acciones sensibles."""
    action_name = _describir_accion(result.intent)
    params_desc = _describir_parametros(result.intent, result.parameters)
    return (
        f"Voy a {action_name} {params_desc}. ¿Confirmas que quieres hacer esto? "
        f"Responde 'sí' o 'no'."
    )


def _coincide_con_patron_rechazo(mensaje: str) -> bool:
    """Verifica si el mensaje coincide con patrones de acciones prohibidas."""
    mensaje_lower = mensaje.lower().strip()
    for patron in PATRONES_RECHAZO:
        if re.search(patron, mensaje_lower):
            return True
    return False


def _describir_accion(intent: IntentType) -> str:
    descripciones = {
        IntentType.OPEN_APP: "abrir",
        IntentType.PLAY_MUSIC: "reproducir música",
        IntentType.PAUSE_MUSIC: "pausar la música",
        IntentType.RESUME_MUSIC: "reanudar la música",
        IntentType.STOP_MUSIC: "detener la música",
        IntentType.VOLUME_UP: "subir el volumen",
        IntentType.VOLUME_DOWN: "bajar el volumen",
    }
    return descripciones.get(intent, intent.value)


def _describir_parametros(intent: IntentType, params: dict) -> str:
    if intent == IntentType.OPEN_APP:
        app_name = params.get("app_name", "")
        entry = ALLOWED_APPS.get(app_name.lower())
        if entry:
            return entry["name"]
        return app_name
    if intent == IntentType.PLAY_MUSIC:
        query = params.get("query", "")
        return f'"{query}"' if query else "música"
    return ""
