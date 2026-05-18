import os
from fastapi import APIRouter, HTTPException, Depends
from google import genai
from sqlalchemy.orm import Session
from .. import schemas, models, utils
from ..database import get_db

router = APIRouter()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Falta configurar GEMINI_API_KEY en el archivo .env")

cliente = genai.Client(api_key=API_KEY)


@router.post("/generar")
def generar_respuesta_ia(
    peticion: schemas.ChatRequest,
    db: Session = Depends(get_db),
    usuario_actual: models.User = Depends(utils.get_usuario_actual),
):
    if peticion.sesion_id:
        sesion = (
            db.query(models.ChatSession)
            .filter(models.ChatSession.id == peticion.sesion_id)
            .first()
        )
        if not sesion or sesion.usuario_id != usuario_actual.id:
            raise HTTPException(
                status_code=404, detail="Sesión no encontrada o no tienes permiso."
            )
    else:
        titulo_generado = peticion.texto[:30] + "..."
        sesion = models.ChatSession(
            usuario_id=usuario_actual.id, titulo=titulo_generado
        )
        db.add(sesion)
        db.commit()
        db.refresh(sesion)

    mensaje_usuario = models.ChatMessage(
        sesion_id=sesion.id, remitente="usuario", contenido=peticion.texto
    )
    db.add(mensaje_usuario)
    db.commit()

    instrucciones_base = "Eres un asistente educativo experto en inclusión escolar para un proyecto STEM+."

    if peticion.modo == "tema":
        modo_prompt = (
            f"Explica el siguiente tema de forma clara y adaptada: '{peticion.texto}'."
        )
    elif peticion.modo == "actividad":
        modo_prompt = f"""Genera un cuestionario interactivo e inclusivo sobre: '{peticion.texto}'.
        DEBES RESPONDER ÚNICA Y EXCLUSIVAMENTE CON UN JSON VÁLIDO. No incluyas texto antes ni después. No uses bloques de código markdown (```json).
        Usa estrictamente esta estructura:
        {{
          "titulo": "Título de la actividad",
          "preguntas": [
            {{
              "pregunta": "Texto de la pregunta",
              "opciones": ["Opción 1", "Opción 2", "Opción 3", "Opción 4"],
              "respuesta_correcta": "Texto exacto de la opción correcta",
              "explicacion": "Breve explicación pedagógica que se mostrará al revelar la respuesta"
            }}
          ]
        }}
        """
    else:
        raise HTTPException(
            status_code=400, detail="Modo no válido. Usa 'tema' o 'actividad'."
        )

    if peticion.rol == "estudiante":
        rol_prompt = "Dirígete directamente al estudiante. Usa un lenguaje motivador, accesible, fácil de entender y amigable."
    elif peticion.rol == "docente":
        rol_prompt = "Dirígete a un profesor. Usa lenguaje pedagógico, sugiere cómo integrar esto en una planeación escolar y menciona adaptaciones curriculares."
    elif peticion.rol == "padre":
        rol_prompt = "Dirígete a un padre de familia. Dale consejos prácticos y sencillos sobre cómo apoyar a su hijo con esta actividad o tema desde casa."
    else:
        raise HTTPException(status_code=400, detail="Rol no válido.")

    prompt_final = f"{instrucciones_base}\n\n{rol_prompt}\n\n{modo_prompt}"

    try:
        respuesta = cliente.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt_final,
        )

        texto_limpio = respuesta.text.strip()

        if peticion.modo == "actividad":
            if texto_limpio.startswith("```json"):
                texto_limpio = texto_limpio[7:]
            if texto_limpio.startswith("```"):
                texto_limpio = texto_limpio[3:]
            if texto_limpio.endswith("```"):
                texto_limpio = texto_limpio[:-3]
            texto_limpio = texto_limpio.strip()

        mensaje_ia = models.ChatMessage(
            sesion_id=sesion.id, remitente="ia", contenido=texto_limpio
        )
        db.add(mensaje_ia)
        db.commit()

        return {"sesion_id": sesion.id, "respuesta_ia": texto_limpio}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al conectar con la IA: {str(e)}"
        )


@router.get("/sesiones")
def obtener_sesiones_usuario(
    db: Session = Depends(get_db),
    usuario_actual: models.User = Depends(utils.get_usuario_actual),
):
    sesiones = (
        db.query(models.ChatSession)
        .filter(models.ChatSession.usuario_id == usuario_actual.id)
        .order_by(models.ChatSession.fecha_creacion.desc())
        .all()
    )
    return sesiones


@router.get("/sesiones/{sesion_id}/mensajes")
def obtener_mensajes_de_sesion(
    sesion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: models.User = Depends(utils.get_usuario_actual),
):
    sesion = (
        db.query(models.ChatSession).filter(models.ChatSession.id == sesion_id).first()
    )
    if not sesion or sesion.usuario_id != usuario_actual.id:
        raise HTTPException(
            status_code=404, detail="La sesión no existe o no tienes acceso a ella."
        )

    mensajes = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.sesion_id == sesion_id)
        .order_by(models.ChatMessage.fecha.asc())
        .all()
    )

    return mensajes
