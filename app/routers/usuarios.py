from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post(
    "/registro", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED
)
def registrar_usuario(usuario: schemas.UserCreate, db: Session = Depends(get_db)):

    usuario_existente = (
        db.query(models.User).filter(models.User.correo == usuario.correo).first()
    )
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este correo ya está registrado.",
        )

    password_encriptada = utils.encriptar_password(usuario.password)

    nuevo_usuario = models.User(
        nombre=usuario.nombre,
        correo=usuario.correo,
        password_hash=password_encriptada,
        rol=usuario.rol,
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/login", response_model=schemas.Token)
def login(
    credenciales: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    usuario = (
        db.query(models.User)
        .filter(models.User.correo == credenciales.username)
        .first()
    )

    if not usuario or not utils.verificar_password(
        credenciales.password, usuario.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )

    token = utils.crear_token_acceso(
        data={"usuario_id": usuario.id, "rol": usuario.rol}
    )

    return {"access_token": token, "token_type": "bearer"}
