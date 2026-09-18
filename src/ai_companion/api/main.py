"""FastAPI server — API REST del AI Companion con soporte SSE streaming."""

import asyncio
import json
from collections.abc import AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from ai_companion.memory import load_history, load_profile, save_history
from ai_companion.models import Turn
from ai_companion.prompts import build_system_prompt
from ai_foundation.utils.logging import logger

from .schemas import (
    ChatRequest,
    ChatResponse,
    EndSessionRequest,
    EndSessionResponse,
    ProfileResponse,
)
from .session_manager import session_manager

app = FastAPI(
    title="AI Companion API",
    description="API REST para el AI Companion con memoria persistente",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health ───────────────────────────────────────────────────────────

@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}


# ─── Chat (respuesta completa) ────────────────────────────────────────

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Envía un mensaje y recibe la respuesta completa."""
    session = session_manager.get_or_create(request.user_id)

    try:
        response_text = await asyncio.to_thread(session.chat, request.message)
    except Exception as e:
        logger.error(f"Error en chat: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar el mensaje")

    return ChatResponse(
        response=response_text,
        user_name=session.profile.name,
    )


# ─── Chat Streaming (SSE) ────────────────────────────────────────────

async def _stream_chat(user_id: str, message: str) -> AsyncGenerator[str, None]:
    """Generador asíncrono que produce tokens SSE desde el LLM."""
    session = session_manager.get_or_create(user_id)
    session.history.append(Turn(role="user", content=message))

    # Construir mensajes
    system_prompt = build_system_prompt(session.profile)
    messages = [SystemMessage(content=system_prompt)]

    from ai_companion.session import MAX_HISTORY_TURNS

    for turn in session.history[-MAX_HISTORY_TURNS:]:
        if turn.role == "user":
            messages.append(HumanMessage(content=turn.content))
        elif turn.role == "assistant":
            messages.append(AIMessage(content=turn.content))

    # Stream tokens
    full_response = ""
    try:
        async for chunk in session.llm.astream(messages):
            token = ""
            if isinstance(chunk.content, list):
                for item in chunk.content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        token = item["text"]
                        break
            elif isinstance(chunk.content, str):
                token = chunk.content

            if token:
                full_response += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
    except Exception as e:
        logger.error(f"Error en streaming: {e}")
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    # Guardar respuesta completa en el historial
    if full_response:
        session.history.append(Turn(role="assistant", content=full_response))
        
    save_history(user_id, session.history)

    # Señal de fin
    yield f"data: {json.dumps({'type': 'done'})}\n\n"


@app.post("/api/v1/chat/stream")
async def chat_stream(request: ChatRequest):
    """Envía un mensaje y recibe tokens como Server-Sent Events."""
    return StreamingResponse(
        _stream_chat(request.user_id, request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ─── Profile & History ──────────────────────────────────────────────────────────

@app.get("/api/v1/profile/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: str):
    """Obtiene el perfil almacenado de un usuario."""
    profile = load_profile(user_id)
    return ProfileResponse(
        user_id=user_id,
        name=profile.name,
        likes=profile.likes,
        events=profile.events,
    )


@app.get("/api/v1/chat/history/{user_id}")
async def get_history(user_id: str):
    """Obtiene el historial de chat completo."""
    history = load_history(user_id)
    return {"history": [t.model_dump() for t in history]}

# ─── Artemis Integration ──────────────────────────────────────────────────

class ArtemisRequest(BaseModel):
    task: str

@app.post("/api/v1/artemis/run")
async def run_artemis_task(req: ArtemisRequest):
    import asyncio
    from ai_foundation.utils.logging import logger
    
    # Artemis toma control del dispositivo conectado por ADB
    # Esta tarea puede ser pesada, por lo que la simulamos o lanzamos en 2do plano.
    async def _execute_artemis():
        logger.info(f"🚀 Iniciando Artemis Agent para: {req.task}")
        try:
            # Ejecutamos el CLI nativo de Artemis configurado en nuestro venv
            # '--profile flash' es más rápido (3-5s por paso)
            process = await asyncio.create_subprocess_exec(
                "artemis", "run", req.task, "--profile", "flash",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"✅ Artemis finalizó la tarea: {req.task}")
                # logger.debug(f"Artemis stdout: {stdout.decode('utf-8', 'ignore')}")
            else:
                logger.error(f"❌ Artemis falló con código {process.returncode}")
                logger.error(f"Stderr: {stderr.decode('utf-8', 'ignore')}")
                
        except Exception as e:
            logger.error(f"❌ Error lanzando Artemis: {e}")

    asyncio.create_task(_execute_artemis())
    return {"status": "started", "task": req.task}



# ─── End Session ──────────────────────────────────────────────────────

@app.post("/api/v1/session/end", response_model=EndSessionResponse)
async def end_session(request: EndSessionRequest):
    """Finaliza la sesión: extrae info del usuario y guarda el perfil."""
    if not session_manager.has_session(request.user_id):
        raise HTTPException(status_code=404, detail="No hay sesión activa para este usuario")

    session = session_manager.get_or_create(request.user_id)

    try:
        await asyncio.to_thread(session_manager.end_session, request.user_id)
    except Exception as e:
        logger.error(f"Error al finalizar sesión: {e}")

    # Recargar el perfil guardado
    saved_profile = load_profile(request.user_id)
    return EndSessionResponse(
        message=f"Sesión finalizada para {request.user_id}",
        profile=ProfileResponse(
            user_id=request.user_id,
            name=saved_profile.name,
            likes=saved_profile.likes,
            events=saved_profile.events,
        ),
    )


# ─── Entry point ─────────────────────────────────────────────────────

def run_server():
    """Punto de entrada para `uv run companion-api`."""
    uvicorn.run(
        "ai_companion.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    run_server()
