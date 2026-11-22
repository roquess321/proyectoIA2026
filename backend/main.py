import asyncio
import importlib.util
import json
import os
import re
import sys
import threading
import time
import traceback
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Asegurar que tanto 'backend' como la raíz del proyecto estén en sys.path
_current_file = Path(__file__).resolve()
_backend_dir = _current_file.parent
_project_root = _backend_dir.parent

for _p in [str(_backend_dir), str(_project_root)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Cargar variables de entorno desde backend/.env o ruta actual
_env_file = _backend_dir / ".env"
if _env_file.exists():
    load_dotenv(dotenv_path=_env_file)
else:
    load_dotenv()

from backend.database import engine, Base, get_db, SessionLocal
from backend.models import ChatSession, ChatMessage, Estudiante, Inscripcion, Parcial, NotaFinal, UsuarioLocal
from backend.schemas import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    MessageItem,
    SessionSummary,
    ScraperSyncRequest,
    ScraperSyncResponse,
    ScraperStatusResponse,
    EstudianteSummaryResponse,
    InscripcionItem,
    ParcialItem,
    NotaFinalItem,
    LoginRequest,
    LoginResponse,
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    LinkInswebRequest,
    DeleteUserDataRequest,
    DeleteUserDataResponse,
    MLPredictRequest,
    MLPredictResponse,
    MLSequentialPredictRequest,
    MLSequentialPredictResponse,
    MLRetrainRequest,
    MLRetrainResponse,
    OfficialScheduleResponse,
)
from backend.services.llm import call_gemini
from backend.services.schedule import cargar_calendario_oficial
from backend.services.scraper import ejecutar_pipeline_estudiante
from backend.services.security import hash_password, verify_password
from backend.services.ml import (
    predecir_aprobacion,
    predecir_serie_temporal,
    obtener_modelos_disponibles,
    reentrenar_modelos_materia,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas en SQLite si no existen aún al arrancar la app
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Copiloto Académico FIUNA - API",
    description="Backend orquestador en FastAPI para el Agente Académico con memoria y persistencia en base de datos.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuración CORS para permitir peticiones desde SvelteKit local y Vercel/HF Spaces
_cors_env = os.getenv("CORS_ORIGINS", "")
_extra_origins = [origin.strip() for origin in _cors_env.split(",") if origin.strip()]
_frontend_url = os.getenv("FRONTEND_URL", "").strip()
if _frontend_url and _frontend_url not in _extra_origins:
    _extra_origins.append(_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        *_extra_origins,
    ],
    allow_origin_regex=r"^https://([a-zA-Z0-9-]+\.)*(vercel\.app|hf\.space)$",
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

    # Limpiar título para que no contenga saltos de línea y tenga longitud adecuada
    clean_title = request.message.strip().splitlines()[0] if request.message.strip() else "Nueva consulta académica"
    title_str = (clean_title[:45] + "...") if len(clean_title) > 45 else clean_title

    # Si no se envió sesión o viene vacía, generar nuevo UUID
    if not session_id:
        session_id = str(uuid.uuid4())
        session = ChatSession(
            id=session_id,
            title=title_str,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    else:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            session = ChatSession(
                id=session_id,
                title=title_str,
            )
            db.add(session)
            db.commit()
            db.refresh(session)

    # Recuperar historial existente de la base de datos (memoria de conversación)
    previous_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )

    history_payload: List[Dict[str, str]] = [
        {"role": str(msg.role), "content": str(msg.content)}
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

    # Construir contexto del estudiante desde la base de datos si se proporciona la cédula
    student_context = None
    if request.cedula:
        clean_ci = request.cedula.strip().replace(".", "")
        usuario = db.query(UsuarioLocal).filter(UsuarioLocal.cedula == clean_ci).first()
        inscripciones = db.query(Inscripcion).filter(Inscripcion.cedula == clean_ci).all()
        notas = db.query(NotaFinal).filter(NotaFinal.cedula == clean_ci).all()
        parciales = (
            db.query(Parcial)
            .filter(Parcial.cedula == clean_ci)
            .order_by(Parcial.periodo.desc(), Parcial.id.asc())
            .all()
        )

        nombre_alumno = usuario.nombre if usuario else f"Estudiante C.I. {clean_ci}"
        carrera_alumno = usuario.carrera if usuario else (inscripciones[0].carrera if inscripciones and inscripciones[0].carrera else "Ingeniería")

        notas_num = [n.nota for n in notas if isinstance(n.nota, int)]
        promedio = round(sum(notas_num) / len(notas_num), 2) if notas_num else 0.0
        aprobadas = len([n for n in notas if n.aprobado])

        materias_en_curso = []
        for ins in inscripciones:
            ins_norm = ins.asignatura.strip().lower()
            exact_matches = [
                p for p in parciales
                if (p.asignatura or "").strip().lower() == ins_norm
            ]
            candidatos = (
                exact_matches
                if exact_matches
                else [
                    p for p in parciales
                    if (p_norm := (p.asignatura or "").strip().lower())
                    and (p_norm in ins_norm or ins_norm in p_norm)
                ]
            )
            latest_periodo = max(((p.periodo or "").strip() for p in candidatos), default="")
            parciales_asig = (
                [p for p in candidatos if (p.periodo or "").strip() == latest_periodo]
                if latest_periodo
                else candidatos
            )
            evals_str = ", ".join([f"{p.tipo_examen}: {p.puntaje if p.puntaje is not None else 'Pendiente'}" for p in parciales_asig])
            periodo_tag = f", Periodo {latest_periodo}" if latest_periodo else ""
            materias_en_curso.append(
                f"- {ins.asignatura} (Semestre {ins.semestre or 'N/A'}{periodo_tag}) -> {evals_str if evals_str else 'Sin evaluaciones cargadas aún'}"
            )

        student_context = (
            f"DATOS OFICIALES DEL ESTUDIANTE:\n"
            f"Nombre: {nombre_alumno}\n"
            f"Cédula: {clean_ci}\n"
            f"Carrera: {carrera_alumno}\n"
            f"Promedio General (PPG): {promedio} / 5.00\n"
            f"Materias Aprobadas: {aprobadas} asignaturas registradas\n\n"
            f"MATERIAS MATRICULADAS EN CURSO ACTIVO:\n"
            + ("\n".join(materias_en_curso) if materias_en_curso else "Ninguna asignatura registrada en curso.")
        )

    # Llamada al LLM con la memoria y contexto recuperado
    try:
        reply_text = await call_gemini(
            history=history_payload,
            new_message=request.message,
            student_context=student_context,
        )
    except Exception as e:
        # En caso de error del proveedor LLM, revertir mensaje para no dejar la sesión en estado inconsistente
        try:
            db.delete(user_msg_record)
            db.commit()
        except Exception:
            db.rollback()
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
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
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


# -----------------------------------------------------------------------------
# ENDPOINTS: SCRAPER E INGESTA ACADÉMICA INSWEB
# -----------------------------------------------------------------------------
_scraper_jobs_lock = threading.Lock()
_active_scraper_jobs = 0


def _inc_scraper_jobs() -> None:
    global _active_scraper_jobs
    with _scraper_jobs_lock:
        _active_scraper_jobs += 1


def _dec_scraper_jobs() -> None:
    global _active_scraper_jobs
    with _scraper_jobs_lock:
        _active_scraper_jobs = max(0, _active_scraper_jobs - 1)


def _get_active_scraper_jobs() -> int:
    with _scraper_jobs_lock:
        return _active_scraper_jobs


@app.get("/api/scraper/status", response_model=ScraperStatusResponse, tags=["Scraper INSWEB"])
async def scraper_status(
    cedula: Optional[str] = None,
    check_insweb: bool = True,
    db: Session = Depends(get_db),
):
    """Retorna telemetría real del motor Playwright, conectividad a INSWEB y estado de SQLite."""
    insweb_url = "https://insweb.ing.una.py/login"
    playwright_ready = importlib.util.find_spec("playwright") is not None

    sqlite_ready = True
    estudiantes_count = 0
    student_synced: Optional[bool] = None
    student_last_sync = None
    student_inscripciones_count: Optional[int] = None
    student_parciales_count: Optional[int] = None
    student_notas_count: Optional[int] = None

    try:
        estudiantes_count = db.query(Estudiante).count()
        if cedula:
            clean_ci = cedula.strip().replace(".", "")
            estudiante = db.query(Estudiante).filter(Estudiante.cedula == clean_ci).first()
            if estudiante:
                student_last_sync = estudiante.fecha_actualizacion
                student_inscripciones_count = (
                    db.query(Inscripcion).filter(Inscripcion.cedula == clean_ci).count()
                )
                student_parciales_count = (
                    db.query(Parcial).filter(Parcial.cedula == clean_ci).count()
                )
                student_notas_count = (
                    db.query(NotaFinal).filter(NotaFinal.cedula == clean_ci).count()
                )
                student_synced = estudiante.fecha_actualizacion is not None or (
                    (student_inscripciones_count or 0)
                    + (student_parciales_count or 0)
                    + (student_notas_count or 0)
                    > 0
                )
            else:
                student_synced = False
                student_inscripciones_count = 0
                student_parciales_count = 0
                student_notas_count = 0
    except Exception:
        sqlite_ready = False

    insweb_reachable: Optional[bool] = None
    insweb_latency_ms: Optional[int] = None
    insweb_status_code: Optional[int] = None

    if check_insweb:
        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                resp = await client.get(insweb_url)
                insweb_latency_ms = round((time.perf_counter() - t0) * 1000)
                insweb_status_code = resp.status_code
                insweb_reachable = resp.status_code < 500
        except Exception:
            insweb_reachable = False
            insweb_latency_ms = None
            insweb_status_code = None

    return ScraperStatusResponse(
        api_online=True,
        playwright_ready=playwright_ready,
        insweb_url=insweb_url,
        insweb_reachable=insweb_reachable,
        insweb_latency_ms=insweb_latency_ms,
        insweb_status_code=insweb_status_code,
        sqlite_ready=sqlite_ready,
        estudiantes_count=estudiantes_count,
        active_jobs=_get_active_scraper_jobs(),
        student_synced=student_synced,
        student_last_sync=student_last_sync,
        student_inscripciones_count=student_inscripciones_count,
        student_parciales_count=student_parciales_count,
        student_notas_count=student_notas_count,
    )


@app.post("/api/scraper/sync", response_model=ScraperSyncResponse, tags=["Scraper INSWEB"])
def sync_insweb(request: ScraperSyncRequest, db: Session = Depends(get_db)):
    """
    Sincroniza y extrae datos académicos en vivo desde INSWEB con Playwright.
    Extrae: inscripciones actuales, notas finales y parciales por periodo.
    """
    clean_ci = request.cedula.strip().replace(".", "")
    _inc_scraper_jobs()
    try:
        res = ejecutar_pipeline_estudiante(
            cedula=clean_ci,
            pin=request.pin,
            db=db,
        )
        conteos = res["conteo"]
        return ScraperSyncResponse(
            ok=True,
            message=f"Datos académicos para C.I. {clean_ci} sincronizados exitosamente.",
            cedula=clean_ci,
            inscripciones_count=conteos["inscripciones"],
            parciales_count=conteos["parciales"],
            notas_count=conteos["notas"],
        )
    except ValueError as e:
        print(f"❌ [Scraper] Error de credenciales en /api/scraper/sync: {e}", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        print(f"❌ [Scraper] Error en /api/scraper/sync: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fallo en la sincronización con INSWEB: {str(e)}",
        )
    finally:
        _dec_scraper_jobs()


@app.get("/api/estudiantes/{cedula}", response_model=EstudianteSummaryResponse, tags=["Estudiantes"])
def obtener_estudiante_completo(cedula: str, db: Session = Depends(get_db)):
    """Retorna la ficha académica completa guardada para la cédula dada."""
    clean_ci = cedula.strip().replace(".", "")
    estudiante = db.query(Estudiante).filter(Estudiante.cedula == clean_ci).first()
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron registros académicos para la C.I. '{clean_ci}'.",
        )
    return EstudianteSummaryResponse.model_validate(estudiante)


@app.get("/api/estudiantes/{cedula}/inscripciones", response_model=List[InscripcionItem], tags=["Estudiantes"])
def obtener_inscripciones_estudiante(cedula: str, db: Session = Depends(get_db)):
    """Retorna las materias matriculadas en el periodo actual."""
    clean_ci = cedula.strip().replace(".", "")
    return db.query(Inscripcion).filter(Inscripcion.cedula == clean_ci).all()


@app.get("/api/estudiantes/{cedula}/parciales", response_model=List[ParcialItem], tags=["Estudiantes"])
def obtener_parciales_estudiante(cedula: str, db: Session = Depends(get_db)):
    """Retorna el historial de evaluaciones parciales y derechos de examen."""
    clean_ci = cedula.strip().replace(".", "")
    return db.query(Parcial).filter(Parcial.cedula == clean_ci).all()


@app.get("/api/estudiantes/{cedula}/notas", response_model=List[NotaFinalItem], tags=["Estudiantes"])
def obtener_notas_estudiante(cedula: str, db: Session = Depends(get_db)):
    """Retorna el historial de notas finales del estudiante."""
    clean_ci = cedula.strip().replace(".", "")
    return db.query(NotaFinal).filter(NotaFinal.cedula == clean_ci).all()


# -----------------------------------------------------------------------------
# ENDPOINTS: AUTENTICACIÓN Y SESIÓN DE ESTUDIANTE
# -----------------------------------------------------------------------------
@app.post("/api/auth/login", response_model=LoginResponse, tags=["Autenticación"])
def login_estudiante(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Inicia sesión de estudiante:
    1. Si el estudiante ya tiene registros en la base de datos, devuelve su perfil.
    2. Si es una nueva vinculación, ejecuta el scraper en modo silencioso.
    """
    clean_ci = request.cedula.strip().replace(".", "")
    estudiante = db.query(Estudiante).filter(Estudiante.cedula == clean_ci).first()

    carrera = request.carrera or "Ingeniería"
    nombre = request.usuario_fiuna or f"Estudiante ({clean_ci})"

    # Si ya tiene registro previo en base de datos
    if estudiante:
        primera_inscripcion = db.query(Inscripcion).filter(Inscripcion.cedula == clean_ci).first()
        if primera_inscripcion and primera_inscripcion.carrera:
            carrera = primera_inscripcion.carrera

        return LoginResponse(
            ok=True,
            cedula=clean_ci,
            nombre=nombre,
            carrera=carrera,
            is_synced=True,
            last_sync=estudiante.fecha_actualizacion,
            message="Sesión iniciada con datos académicos en base de datos.",
        )

    # Si no existe aún en la base de datos, sincronizar con el scraper
    try:
        ejecutar_pipeline_estudiante(cedula=clean_ci, pin=request.pin, db=db)
        estudiante_nuevo = db.query(Estudiante).filter(Estudiante.cedula == clean_ci).first()
        primera_inscripcion = db.query(Inscripcion).filter(Inscripcion.cedula == clean_ci).first()
        if primera_inscripcion and primera_inscripcion.carrera:
            carrera = primera_inscripcion.carrera

        return LoginResponse(
            ok=True,
            cedula=clean_ci,
            nombre=nombre,
            carrera=carrera,
            is_synced=True,
            last_sync=estudiante_nuevo.fecha_actualizacion if estudiante_nuevo else None,
            message="Sesión iniciada y sincronizada exitosamente con INSWEB.",
        )
    except Exception as e:
        # En caso de error de conexión en INSWEB, permitir acceso local informando estado
        return LoginResponse(
            ok=True,
            cedula=clean_ci,
            nombre=nombre,
            carrera=carrera,
            is_synced=False,
            last_sync=None,
            message=f"Sesión iniciada en modo local (Aviso INSWEB: {str(e)})",
        )


@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Autenticación Local"])
def registrar_usuario(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """Crea una nueva cuenta de usuario local con contraseña hasheada y vinculada por Cédula única."""
    clean_username = request.usuario.strip().lower()
    clean_ci = re.sub(r"[^0-9]", "", request.cedula)

    if len(clean_ci) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La Cédula de Identidad debe contener al menos 3 dígitos.",
        )

    # Verificar si el nombre de usuario ya está tomado
    existe = db.query(UsuarioLocal).filter(UsuarioLocal.usuario == clean_username).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El nombre de usuario '{clean_username}' ya está registrado.",
        )

    # Verificar unicidad por Cédula de Identidad para impedir doble cuenta por persona
    existe_cedula = db.query(UsuarioLocal).filter(UsuarioLocal.cedula == clean_ci).first()
    if existe_cedula:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"La Cédula de Identidad '{clean_ci}' ya tiene una cuenta registrada. "
                "Inicia sesión con tu cuenta existente en lugar de crear otra."
            ),
        )

    # Asegurar que el registro de estudiante existe para enlazar la ForeignKey
    estudiante = db.query(Estudiante).filter(Estudiante.cedula == clean_ci).first()
    if not estudiante:
        estudiante = Estudiante(cedula=clean_ci)
        db.add(estudiante)
        db.flush()

    nuevo_usuario = UsuarioLocal(
        usuario=clean_username,
        password_hash=hash_password(request.password),
        cedula=clean_ci,
        nombre=request.nombre.strip(),
        carrera=request.carrera or "Ingeniería",
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    is_synced = estudiante.fecha_actualizacion is not None

    return UserResponse(
        ok=True,
        id=nuevo_usuario.id,
        usuario=nuevo_usuario.usuario,
        cedula=nuevo_usuario.cedula,
        nombre=nuevo_usuario.nombre,
        carrera=nuevo_usuario.carrera,
        is_synced=is_synced,
        last_sync=estudiante.fecha_actualizacion,
        message="Usuario registrado exitosamente en la base de datos local.",
    )


@app.post("/api/auth/login-local", response_model=UserResponse, tags=["Autenticación Local"])
def login_local(request: UserLoginRequest, db: Session = Depends(get_db)):
    """Inicia sesión con cuenta local verificando credenciales hasheadas."""
    ident = request.identificador.strip().lower()
    ident_ci = re.sub(r"[^0-9]", "", request.identificador)

    # Buscar primero por nombre de usuario único
    usuario = db.query(UsuarioLocal).filter(UsuarioLocal.usuario == ident).first()
    if usuario and not verify_password(request.password, usuario.password_hash):
        usuario = None

    # Si no coincidió por usuario y el identificador contiene dígitos de C.I., buscar entre cuentas con esa cédula
    if not usuario and ident_ci:
        candidatos = db.query(UsuarioLocal).filter(UsuarioLocal.cedula == ident_ci).all()
        for candidato in candidatos:
            if verify_password(request.password, candidato.password_hash):
                usuario = candidato
                break

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas. Verifica tu usuario o contraseña.",
        )

    # Revisar estado de sincronización del estudiante
    estudiante = db.query(Estudiante).filter(Estudiante.cedula == usuario.cedula).first()
    is_synced = estudiante is not None and estudiante.fecha_actualizacion is not None
    last_sync = estudiante.fecha_actualizacion if estudiante else None

    return UserResponse(
        ok=True,
        id=usuario.id,
        usuario=usuario.usuario,
        cedula=usuario.cedula,
        nombre=usuario.nombre,
        carrera=usuario.carrera,
        is_synced=is_synced,
        last_sync=last_sync,
        message="Inicio de sesión exitoso.",
    )


@app.post("/api/auth/link-insweb", response_model=ScraperSyncResponse, tags=["Autenticación Local"])
def link_insweb(request: LinkInswebRequest, db: Session = Depends(get_db)):
    """Ejecuta el scraper silencioso y asocia las materias/notas a la cédula de la cuenta."""
    clean_ci = request.cedula.strip().replace(".", "")
    _inc_scraper_jobs()
    try:
        resultado = ejecutar_pipeline_estudiante(cedula=clean_ci, pin=request.pin, db=db)
        conteos = resultado["conteo"]
        return ScraperSyncResponse(
            ok=True,
            message=f"Datos académicos sincronizados correctamente para C.I. {clean_ci}.",
            cedula=clean_ci,
            inscripciones_count=conteos["inscripciones"],
            parciales_count=conteos["parciales"],
            notas_count=conteos["notas"],
        )
    except ValueError as e:
        print(f"❌ [Scraper] Error de credenciales en /api/auth/link-insweb: {e}", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        print(f"❌ [Scraper] Error en /api/auth/link-insweb: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fallo al sincronizar con INSWEB: {str(e)}",
        )
    finally:
        _dec_scraper_jobs()


@app.post("/api/auth/delete-data", response_model=DeleteUserDataResponse, tags=["Autenticación Local"])
def eliminar_datos_usuario(request: DeleteUserDataRequest, db: Session = Depends(get_db)):
    """Elimina todos los datos académicos, snapshot JSON y opcionalmente la cuenta local tras validar contraseña."""
    clean_ci = re.sub(r"[^0-9]", "", request.cedula)
    if len(clean_ci) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La Cédula de Identidad debe contener al menos 3 dígitos.",
        )

    usuario_valido: Optional[UsuarioLocal] = None
    if request.usuario and request.usuario.strip():
        clean_user = request.usuario.strip().lower()
        candidato = db.query(UsuarioLocal).filter(UsuarioLocal.usuario == clean_user).first()
        if (
            candidato
            and candidato.cedula == clean_ci
            and verify_password(request.password, candidato.password_hash)
        ):
            usuario_valido = candidato
    else:
        candidatos = db.query(UsuarioLocal).filter(UsuarioLocal.cedula == clean_ci).all()
        for candidato in candidatos:
            if verify_password(request.password, candidato.password_hash):
                usuario_valido = candidato
                break

    if not usuario_valido:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta. No se eliminaron los datos.",
        )

    inscripciones_deleted = (
        db.query(Inscripcion).filter(Inscripcion.cedula == clean_ci).delete(synchronize_session=False)
    )
    parciales_deleted = (
        db.query(Parcial).filter(Parcial.cedula == clean_ci).delete(synchronize_session=False)
    )
    notas_deleted = (
        db.query(NotaFinal).filter(NotaFinal.cedula == clean_ci).delete(synchronize_session=False)
    )
    db.query(Estudiante).filter(Estudiante.cedula == clean_ci).delete(synchronize_session=False)

    account_deleted = False
    if request.eliminar_cuenta:
        db.delete(usuario_valido)
        account_deleted = True

    db.commit()

    snapshot_deleted = False
    for snap_path in {
        (_project_root / "data" / f"insweb_raw_{clean_ci}.json").resolve(),
        (Path("data") / f"insweb_raw_{clean_ci}.json").resolve(),
    }:
        if snap_path.is_file():
            try:
                snap_path.unlink()
                snapshot_deleted = True
            except OSError:
                pass

    return DeleteUserDataResponse(
        ok=True,
        cedula=clean_ci,
        inscripciones_deleted=inscripciones_deleted,
        parciales_deleted=parciales_deleted,
        notas_deleted=notas_deleted,
        account_deleted=account_deleted,
        snapshot_deleted=snapshot_deleted,
        message=(
            f"Todos tus datos académicos para C.I. {clean_ci} "
            f"({'y tu cuenta local ' if account_deleted else ''}"
            "fueron eliminados definitivamente)."
        ),
    )


@app.post("/api/auth/link-insweb/stream", tags=["Autenticación Local"])
async def link_insweb_stream(request: LinkInswebRequest):
    """Ejecuta el scraper silencioso transmitiendo telemetría en vivo vía Server-Sent Events (SSE)."""
    clean_ci = request.cedula.strip().replace(".", "")
    pin = request.pin

    async def event_generator():
        queue: asyncio.Queue[Optional[Dict[str, Any]]] = asyncio.Queue()
        loop = asyncio.get_running_loop()
        state_ref: Dict[str, str] = {"last_step": "handshake"}

        def push(ev: Optional[Dict[str, Any]]) -> None:
            if isinstance(ev, dict) and isinstance(ev.get("step"), str):
                state_ref["last_step"] = ev["step"]
            loop.call_soon_threadsafe(queue.put_nowait, ev)

        def worker() -> None:
            _inc_scraper_jobs()
            thread_db = SessionLocal()
            try:
                resultado = ejecutar_pipeline_estudiante(
                    cedula=clean_ci,
                    pin=pin,
                    db=thread_db,
                    on_progress=push,
                )
                conteos = resultado["conteo"]
                push(
                    {
                        "type": "complete",
                        "ok": True,
                        "cedula": clean_ci,
                        "message": f"Datos académicos sincronizados correctamente para C.I. {clean_ci}.",
                        "inscripciones_count": conteos["inscripciones"],
                        "parciales_count": conteos["parciales"],
                        "notas_count": conteos["notas"],
                        "progress": 100,
                    }
                )
            except Exception as exc:
                print(f"❌ [Scraper] Error en /api/auth/link-insweb/stream: {exc}", flush=True)
                traceback.print_exc()
                push(
                    {
                        "type": "error",
                        "ok": False,
                        "detail": str(exc),
                        "step": state_ref["last_step"],
                        "step_status": "error",
                    }
                )
            finally:
                try:
                    thread_db.close()
                except Exception:
                    pass
                _dec_scraper_jobs()
                push(None)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=15.0)
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"
                continue

            if item is None:
                break
            yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# --- Endpoints de Herramientas de IA y Machine Learning ---

@app.post("/api/ml/predict", response_model=MLPredictResponse, tags=["Machine Learning"])
def predecir_aprobacion_endpoint(req: MLPredictRequest):
    """
    Calcula la probabilidad de aprobación de un estudiante con los 3 modelos
    del Primer Parcial (Regresión Logística, Árbol de Decisión y Random Forest).
    """
    try:
        resultado = predecir_aprobacion(
            materia=req.materia,
            primer_parcial=req.primer_parcial,
            segundo_parcial=req.segundo_parcial,
            tplab=req.tplab
        )
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular la predicción de Machine Learning: {str(e)}"
        )


@app.post("/api/ml/predict-sequential", response_model=MLSequentialPredictResponse, tags=["Machine Learning"])
def predecir_serie_temporal_endpoint(req: MLSequentialPredictRequest):
    """
    Predice la probabilidad de aprobación a lo largo de la serie temporal del semestre.
    Permite hacer predicciones en cualquier momento después del Primer Parcial:
    - Hito 1: Inmediatamente después del 1er Parcial (solo 'primer_parcial').
    - Hito 2: Tras entrega de TP / Taller ('primer_parcial' + 'tplab').
    - Hito 3: Proceso completo ('primer_parcial' + 'tplab' + 'segundo_parcial').
    """
    try:
        resultado = predecir_serie_temporal(
            materia=req.materia,
            primer_parcial=req.primer_parcial,
            tplab=req.tplab,
            segundo_parcial=req.segundo_parcial,
        )
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular la predicción secuencial de serie temporal: {str(e)}"
        )


@app.get("/api/horarios/examenes", response_model=OfficialScheduleResponse, tags=["Horarios Oficiales"])
def obtener_horarios_examenes(
    cedula: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Lee el calendario oficial de exámenes desde data/horarios_oficiales/calendario_examenes.json.
    Si se envía `cedula`, filtra los exámenes correspondientes a la carrera y asignaturas inscritas del estudiante.
    """
    inscripciones_asigs: Optional[List[str]] = None
    carreras_alumno: List[str] = []
    if cedula and cedula.strip():
        clean_ci = cedula.strip().replace(".", "")
        rows = db.query(Inscripcion).filter(Inscripcion.cedula == clean_ci).all()
        if rows:
            inscripciones_asigs = [r.asignatura for r in rows if r.asignatura]
            carreras_alumno.extend([r.carrera for r in rows if r.carrera])
        usuario = db.query(UsuarioLocal).filter(UsuarioLocal.cedula == clean_ci).first()
        if usuario and usuario.carrera:
            carreras_alumno.append(usuario.carrera)

    return cargar_calendario_oficial(
        inscripciones=inscripciones_asigs,
        carreras_alumno=carreras_alumno or None,
    )


@app.get("/api/ml/models", tags=["Machine Learning"])
def listar_modelos_ml():
    """
    Retorna la lista de modelos entrenados disponibles (del 1er parcial y preparados para el 2do parcial).
    """
    return obtener_modelos_disponibles()


@app.post("/api/ml/retrain", response_model=MLRetrainResponse, tags=["Machine Learning"])
def reentrenar_modelos_ml_endpoint(req: MLRetrainRequest):
    """
    Reentrena los 5 modelos (Regresión Logística, Árbol de Decisión, Random Forest,
    Serie Temporal Gradient Boosting y Red Neuronal LSTM) específicamente para la asignatura indicada.
    """
    try:
        return reentrenar_modelos_materia(req.materia)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al reentrenar los modelos para '{req.materia}': {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)




