"""Interfaz base para acciones del agente."""

from abc import ABC, abstractmethod
from ..models import IntentResult, ActionResult


class BaseAction(ABC):
    """Clase base para todas las acciones del agente."""

    @abstractmethod
    async def execute(self, intent: IntentResult) -> ActionResult:
        """Ejecuta la acción con los parámetros de la intención."""
