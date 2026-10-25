from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class MessageItem(BaseModel):
    role: str = Field(..., description="Rol del emisor: 'user' o 'model'")
    content: str = Field(..., description="Contenido textual del mensaje")
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Pregunta o consulta del estudiante")
    session_id: Optional[str] = Field(None, description="ID opcional de sesión existente. Si no se envía, se crea una nueva.")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Respuesta generada por el Agente LLM")
    session_id: str = Field(..., description="ID de la sesión de chat asociada")


class SessionSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    session_id: str
    title: str
    messages: List[MessageItem]
