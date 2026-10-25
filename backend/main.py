import os
import uuid
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Cargar variables de entorno desde backend/.env o ruta actual
_backend_dir = os.path.dirname(os.path.abspath(__file__))
_env_file = os.path.join(_backend_dir, ".env")
if os.path.exists(_env_file):
    load_dotenv(dotenv_path=_env_file)
else:
    load_dotenv()

try:
    from .database import engine, Base, get_db
    from .models import ChatSession, ChatMessage
    from .schemas import (
        ChatRequest,
        ChatResponse,
        HistoryResponse,
        MessageItem,
        SessionSummary,
    )
    from .services.llm import call_gemini
except ImportError:
    from database import engine, Base, get_db
    from models import ChatSession, ChatMessage
    from schemas import (
        ChatRequest,
        ChatResponse,
        HistoryResponse,
        MessageItem,
        SessionSummary,
    )
    from services.llm import call_gemini


# Crear tablas en SQLite si no existen aún
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Copiloto Académico FIUNA - API",
    description="Backend orquestador en FastAPI para el Agente Académico con memoria y persistencia en base de datos.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuración CORS para permitir peticiones desde la app Svelte (puerto 5173 / 4173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "*",  # Permite pruebas locales abiertas
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": "Copiloto Académico FIUNA API",
        "version": "1.0.0",
        "docs_url": "/docs",
    }


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal del Agente:
    1. Recupera o crea la sesión en base de datos.
    2. Carga el historial previo para proveer memoria contextual al LLM.
    3. Guarda el mensaje del estudiante en la base de datos.
    4. Consulta al proveedor LLM (Gemini) con la clave protegida en el servidor.
    5. Guarda la respuesta generada en la base de datos y la retorna al cliente.
    """
    session_id = request.session_id

    # Si no se envió sesión o viene vacía, generar nuevo UUID
    if not session_id:
        session_id = str(uuid.uuid4())
        session = ChatSession(
            id=session_id,
            title=(request.message[:45] + "...") if len(request.message) > 45 else request.message,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    else:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            session = ChatSession(
                id=session_id,
                title=(request.message[:45] + "...") if len(request.message) > 45 else request.message,
            )
            db.add(session)
            db.commit()
            db.refresh(session)

    # Recuperar historial existente de la base de datos (memoria de conversación)
    previous_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    history_payload = [
        {"role": msg.role, "content": msg.content}
        for msg in previous_messages
    ]

    # Guardar mensaje del usuario en la base de datos antes de la llamada
    user_msg_record = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.message,
    )
    db.add(user_msg_record)
    db.commit()

    # Llamada al LLM con la memoria recuperada
    try:
        reply_text = await call_gemini(history=history_payload, new_message=request.message)
    except Exception as e:
        # En caso de error del proveedor LLM, revertir o notificar
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Fallo al comunicarse con el proveedor de IA: {str(e)}",
        )

    # Guardar respuesta del asistente en la base de datos
    model_msg_record = ChatMessage(
        session_id=session.id,
        role="model",
        content=reply_text,
    )
    db.add(model_msg_record)
    db.commit()

    return ChatResponse(reply=reply_text, session_id=session.id)


@app.get("/api/chat/history/{session_id}", response_model=HistoryResponse, tags=["Chat"])
def get_history(session_id: str, db: Session = Depends(get_db)):
    """Devuelve todo el historial de mensajes de una conversación almacenado en la BD."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return HistoryResponse(
        session_id=session.id,
        title=session.title,
        messages=[
            MessageItem(role=msg.role, content=msg.content, created_at=msg.created_at)
            for msg in messages
        ],
    )


@app.get("/api/chat/sessions", response_model=List[SessionSummary], tags=["Chat"])
def list_sessions(db: Session = Depends(get_db)):
    """Lista todas las sesiones activas en la base de datos con su conteo de mensajes."""
    sessions = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()
    result = []
    for s in sessions:
        count = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).count()
        result.append(
            SessionSummary(
                id=s.id,
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=count,
            )
        )
    return result


@app.delete("/api/chat/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Chat"])
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Elimina una sesión y todo su historial de la base de datos."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")
    db.delete(session)
    db.commit()
    return None
