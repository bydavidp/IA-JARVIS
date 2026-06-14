"""Modelos Pydantic para intenciones y acciones del agente."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    CHAT = "chat"
    OPEN_APP = "open_app"
    PLAY_MUSIC = "play_music"
    PAUSE_MUSIC = "pause_music"
    RESUME_MUSIC = "resume_music"
    STOP_MUSIC = "stop_music"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    HELP = "help"
    STATUS = "status"
    REJECT = "reject"
    UNKNOWN = "unknown"


class IntentResult(BaseModel):
    intent: IntentType = IntentType.UNKNOWN
    parameters: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    original_message: str = ""
    explanation: str = ""


class ActionResult(BaseModel):
    success: bool = False
    message: str = ""
    data: dict[str, Any] = Field(default_factory=dict)
    requires_confirmation: bool = False


class ConfirmationRequest(BaseModel):
    action: str
    parameters: dict[str, Any]
    message: str
    requires_input: bool = False
