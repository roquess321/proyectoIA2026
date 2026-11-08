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
    cedula: Optional[str] = Field(None, description="Número de Cédula del estudiante para consultar su historial y notas en SQLite")


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


# Esquemas para Scraper y Datos Académicos
class ScraperSyncRequest(BaseModel):
    cedula: str = Field(..., min_length=4, description="Número de Cédula de Identidad")
    pin: str = Field(..., min_length=1, description="PIN o contraseña de acceso a INSWEB")


class ScraperSyncResponse(BaseModel):
    ok: bool
    message: str
    cedula: str
    inscripciones_count: int = 0
    parciales_count: int = 0
    notas_count: int = 0


class InscripcionItem(BaseModel):
    carrera: Optional[str] = None
    asignatura: str
    semestre: Optional[str] = None
    estado: Optional[str] = None

    class Config:
        from_attributes = True


class ParcialItem(BaseModel):
    asignatura: str
    tipo_examen: str
    puntaje: Optional[float] = None
    periodo: Optional[str] = None

    class Config:
        from_attributes = True


class NotaFinalItem(BaseModel):
    asignatura: str
    nota: Optional[int] = None
    nota_literal: Optional[str] = None
    fecha: Optional[str] = None
    nro_acta: Optional[str] = None
    tipo: Optional[str] = None
    aprobado: bool = False

    class Config:
        from_attributes = True


class EstudianteSummaryResponse(BaseModel):
    cedula: str
    fecha_actualizacion: Optional[datetime] = None
    inscripciones: List[InscripcionItem] = []
    parciales: List[ParcialItem] = []
    notas: List[NotaFinalItem] = []


class LoginRequest(BaseModel):
    cedula: str = Field(..., min_length=3, description="Cédula de Identidad")
    pin: str = Field(..., min_length=1, description="PIN o contraseña de INSWEB")
    usuario_fiuna: Optional[str] = None
    carrera: Optional[str] = None


class LoginResponse(BaseModel):
    ok: bool
    cedula: str
    nombre: str
    carrera: str
    is_synced: bool
    last_sync: Optional[datetime] = None
    message: str


# Modelos para Cuentas Locales Independientes
class UserRegisterRequest(BaseModel):
    usuario: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario o alias")
    password: str = Field(..., min_length=4, description="Contraseña de la cuenta local")
    cedula: str = Field(..., min_length=3, max_length=30, description="Cédula de Identidad para vinculación académica")
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo del estudiante")
    carrera: Optional[str] = Field("Ingeniería Electromecánica", description="Carrera de grado")


class UserLoginRequest(BaseModel):
    identificador: str = Field(..., min_length=3, description="Nombre de usuario o Cédula de Identidad")
    password: str = Field(..., min_length=1, description="Contraseña local")


class UserResponse(BaseModel):
    ok: bool
    id: int
    usuario: str
    cedula: str
    nombre: str
    carrera: str
    is_synced: bool
    last_sync: Optional[datetime] = None
    message: str


class LinkInswebRequest(BaseModel):
    cedula: str = Field(..., min_length=3, description="Cédula de Identidad")
    pin: str = Field(..., min_length=1, description="PIN de acceso a INSWEB")


# Modelos para Predicción de Machine Learning (1er y 2do Parcial)
class MLPredictRequest(BaseModel):
    materia: str = Field("ESTATICA", description="Nombre o patrón de la asignatura a predecir")
    primer_parcial: float = Field(..., ge=0, le=100, description="Puntaje del 1er Parcial")
    segundo_parcial: float = Field(..., ge=0, le=100, description="Puntaje del 2do Parcial")
    tplab: float = Field(..., ge=0, le=100, description="Puntaje de Taller / Laboratorio / TP")


class ModeloProbabilidadItem(BaseModel):
    nombre: str
    probabilidad: float = Field(..., description="Probabilidad en porcentaje (0 a 100)")
    prediccion: str = Field(..., description="'Aprueba' o 'No Aprueba'")
    descripcion: str


class MLResumenPrediccion(BaseModel):
    probabilidad_promedio: float
    diagnostico: str
    recomendacion: str


class MLPredictResponse(BaseModel):
    materia: str
    materia_modelo: str
    parcial_origen: str
    inputs: dict
    probabilidades: dict
    resumen: MLResumenPrediccion


