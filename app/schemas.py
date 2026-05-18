from pydantic import BaseModel, EmailStr
from .models import UserRole
from typing import Optional


class UserCreate(BaseModel):
    nombre: str
    correo: EmailStr
    password: str
    rol: UserRole


class UserOut(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    rol: UserRole

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    correo: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ChatRequest(BaseModel):
    texto: str
    modo: str
    rol: str
    sesion_id: Optional[int] = None
