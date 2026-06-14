from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
import json

from ...services.chat_service import chat_service, SYSTEM_PROMPTS

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Request para el endpoint de chat."""
    message: str
    mode: str = "general"  # general, code, math, networks
    context: Optional[str] = None


class ChatMode(BaseModel):
    """Información de un modo disponible."""
    name: str
    description: str


@router.post("")
async def chat(request: ChatRequest) -> StreamingResponse:
    """
    Endpoint principal de chat con streaming de respuestas.

    El modo determina el comportamiento del asistente:
    - general: Conversación normal y conceptos generales
    - code: Análisis y explicación de código
    - math: Problemas y conceptos matemáticos
    - networks: Temas de redes y sistemas
    """
    if request.mode not in SYSTEM_PROMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Modo inválido. Modos disponibles: {list(SYSTEM_PROMPTS.keys())}"
        )

    async def generate_response() -> AsyncGenerator[str, None]:
        try:
            async for token in chat_service.chat(
                message=request.message,
                mode=request.mode,
                context=request.context
            ):
                # Formato SSE (Server-Sent Events)
                yield f"data: {json.dumps({'token': token})}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )



