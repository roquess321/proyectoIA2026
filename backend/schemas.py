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


class ScraperStatusResponse(BaseModel):
    api_online: bool = True
    playwright_ready: bool
    insweb_url: str
    insweb_reachable: Optional[bool] = None
    insweb_latency_ms: Optional[int] = None
    insweb_status_code: Optional[int] = None
    sqlite_ready: bool
    estudiantes_count: int = 0
    active_jobs: int = 0
    student_synced: Optional[bool] = None
    student_last_sync: Optional[datetime] = None
    student_inscripciones_count: Optional[int] = None
    student_parciales_count: Optional[int] = None
    student_notas_count: Optional[int] = None


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

    class Config:
        from_attributes = True


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


class DeleteUserDataRequest(BaseModel):
    usuario: Optional[str] = Field(None, description="Nombre de usuario local autenticado")
    cedula: str = Field(..., min_length=3, max_length=30, description="Cédula de Identidad a eliminar")
    password: str = Field(..., min_length=1, description="Contraseña local para confirmar identidad")
    eliminar_cuenta: bool = Field(True, description="Si es True, elimina también la cuenta local de acceso")


class DeleteUserDataResponse(BaseModel):
    ok: bool
    cedula: str
    inscripciones_deleted: int
    parciales_deleted: int
    notas_deleted: int
    account_deleted: bool
    snapshot_deleted: bool
    message: str


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
    probabilidad_modelos_clasicos: Optional[float] = None
    probabilidad_modelos_temporales: Optional[float] = None
    analisis_serie_temporal: Optional[dict] = None



class MLPredictResponse(BaseModel):
    materia: str
    materia_modelo: str
    parcial_origen: str
    inputs: dict
    probabilidades: dict
    resumen: MLResumenPrediccion


# Modelos para Predicción Secuencial / Serie Temporal Progresiva
class MLSequentialPredictRequest(BaseModel):
    materia: str = Field("ESTATICA", description="Nombre de la asignatura (ej: 'ESTATICA')")
    primer_parcial: float = Field(..., ge=0, le=100, description="Puntaje obtenido en el 1er Parcial (0 a 100)")
    tplab: Optional[float] = Field(None, ge=0, le=100, description="Puntaje de Trabajo Práctico / Taller / Lab (opcional)")
    segundo_parcial: Optional[float] = Field(None, ge=0, le=100, description="Puntaje del 2do Parcial (opcional)")


class MLSequentialPredictResponse(BaseModel):
    materia: str
    materia_slug: str
    etapa_temporal: int = Field(..., description="1: Post 1er Parcial, 2: Post TP/Lab, 3: Proceso Completo")
    hito: str
    evaluaciones_registradas: dict
    probabilidad_aprobacion: float = Field(..., description="Probabilidad en porcentaje (0 a 100)")
    estado_trayectoria: str
    tendencia: str
    puntos_acumulados_promedio: float
    proyeccion_siguiente_evaluacion: dict
    diagnostico: str
    recomendacion: str
    comparativa_modelos: Optional[dict] = Field(None, description="Comparativa entre Ensamble Clásico (Gradient Boosting) y Red Neuronal Recurrente (LSTM)")


class MLRetrainRequest(BaseModel):
    materia: str = Field(..., min_length=2, description="Nombre de la asignatura para reentrenar los 5 modelos ML/LSTM")


class MLRetrainResponse(BaseModel):
    ok: bool
    materia: str
    materia_slug: str
    materia_dataset: str
    fallback_global: bool = False
    total_muestras: int
    duracion_seg: float
    metricas: dict
    mensaje: str


class OfficialExamItem(BaseModel):
    id: str
    asignatura: str
    instancia: str
    fecha: str
    month: str
    day: str
    title: str
    subtitle: str
    days_remaining: int
    time: str
    urgency: str


class OfficialScheduleResponse(BaseModel):
    source: str
    periodo: Optional[str] = None
    fuente: str
    actualizado_en: Optional[str] = None
    archivo: str
    examenes: List[OfficialExamItem] = []




