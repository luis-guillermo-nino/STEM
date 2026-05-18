from fastapi import FastAPI
from app.routers import usuarios,ia
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Aula Inclusiva", description="Backend para el sistema", version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=True,
    allow_methods=["*"],            
    allow_headers=["*"],         
)

@app.get("/")
def read_root():
    return {"status": "online"}


app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(ia.router, prefix="/api/ia", tags=["Inteligencia Artificial"]) 