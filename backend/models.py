from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
try:
    from .database import Base
except ImportError:
    from database import Base


class ChatSession(Base):
    """Representa una sesión o hilo de conversación con el Copiloto."""
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), default="Nueva consulta académica")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.id")


class ChatMessage(Base):
    """Representa un mensaje individual (usuario o asistente) dentro de una sesión."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' o 'model' / 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("ChatSession", back_populates="messages")


class Estudiante(Base):
    """Representa a un estudiante de FIUNA identificado por su C.I."""
    __tablename__ = "estudiantes"

    cedula = Column(String(30), primary_key=True, index=True)
    fecha_actualizacion = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    inscripciones = relationship("Inscripcion", back_populates="estudiante", cascade="all, delete-orphan")
    parciales = relationship("Parcial", back_populates="estudiante", cascade="all, delete-orphan")
    notas = relationship("NotaFinal", back_populates="estudiante", cascade="all, delete-orphan")


class Inscripcion(Base):
    """Materia matriculada en el periodo académico."""
    __tablename__ = "inscripciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cedula = Column(String(30), ForeignKey("estudiantes.cedula", ondelete="CASCADE"), nullable=False, index=True)
    carrera = Column(String(100), nullable=True)
    asignatura = Column(String(200), nullable=False)
    semestre = Column(String(50), nullable=True)
    estado = Column(String(50), nullable=True)

    estudiante = relationship("Estudiante", back_populates="inscripciones")


class Parcial(Base):
    """Evaluación parcial o derecho a examen."""
    __tablename__ = "parciales"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cedula = Column(String(30), ForeignKey("estudiantes.cedula", ondelete="CASCADE"), nullable=False, index=True)
    asignatura = Column(String(200), nullable=False)
    tipo_examen = Column(String(100), nullable=False)
    puntaje = Column(Float, nullable=True)
    periodo = Column(String(50), nullable=True)

    estudiante = relationship("Estudiante", back_populates="parciales")


class NotaFinal(Base):
    """Calificación final de una materia."""
    __tablename__ = "notas_finales"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cedula = Column(String(30), ForeignKey("estudiantes.cedula", ondelete="CASCADE"), nullable=False, index=True)
    asignatura = Column(String(200), nullable=False)
    nota = Column(Integer, nullable=True)
    nota_literal = Column(String(50), nullable=True)
    fecha = Column(String(50), nullable=True)
    nro_acta = Column(String(50), nullable=True)
    tipo = Column(String(50), nullable=True)
    aprobado = Column(Boolean, default=False)

    estudiante = relationship("Estudiante", back_populates="notas")


class UsuarioLocal(Base):
    """Cuenta de usuario local independiente con credenciales seguras."""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    cedula = Column(String(30), ForeignKey("estudiantes.cedula", ondelete="SET NULL"), nullable=True, index=True)
    nombre = Column(String(100), nullable=False)
    carrera = Column(String(100), default="Ingeniería")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    estudiante = relationship("Estudiante", backref="usuarios_locales")

