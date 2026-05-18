from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base
import enum


class UserRole(str, enum.Enum):
    PADRE = "padre"
    ESTUDIANTE = "estudiante"
    DOCENTE = "docente"


class User(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(Enum(UserRole), nullable=False)


class ChatSession(Base):
    __tablename__ = "sesiones_chat"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    titulo = Column(String, default="Nuevo Chat")
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    usuario = relationship("User")
    mensajes = relationship(
        "ChatMessage", back_populates="sesion", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    __tablename__ = "mensajes_chat"

    id = Column(Integer, primary_key=True, index=True)
    sesion_id = Column(
        Integer, ForeignKey("sesiones_chat.id", ondelete="CASCADE"), nullable=False
    )
    remitente = Column(String, nullable=False)
    contenido = Column(Text, nullable=False)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    sesion = relationship("ChatSession", back_populates="mensajes")
