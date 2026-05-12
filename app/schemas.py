from pydantic import BaseModel, EmailStr
from .models import UserRole


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
