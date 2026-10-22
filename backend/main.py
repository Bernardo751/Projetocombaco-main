from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rotas import clientes, senioridade, tatuadores, agendamentos
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)   # garante que a pasta existe antes de tentar servir arquivos dela
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")   # ← serve as imagens

app.include_router(clientes.router)
app.include_router(senioridade.router)
app.include_router(tatuadores.router)
app.include_router(agendamentos.router)


@app.get("/")
def home():
    return {"mensagem": "API do estudo de tatuagem funcionando!"}