from sqlalchemy import Column, Integer, String, Enum
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
