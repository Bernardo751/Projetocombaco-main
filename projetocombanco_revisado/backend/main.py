# ============================================================
# main.py — API do sistema de gestão do estúdio
# Como rodar: uvicorn main:app --reload
# ============================================================
import os

from fastapi.responses import JSONResponse

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mysql.connector import IntegrityError, InterfaceError, OperationalError

from seguranca import verificar_token, verificar_admin
from rotas import (
    agendamentos,
    clientes,
    estilos,
    login,
    senioridade,
    tatuadores,
    usuarios,
)

load_dotenv()

app = FastAPI(
    title="Estúdio de Tatuagem API",
    version="1.1.0",
    openapi_tags=[
        {"name": nome}
        for nome in [
            "Login",
            "Usuários",
            "Clientes",
            "Senioridade",
            "Estilos",
            "Tatuadores",
            "Agendamentos",
            "Início",
        ]
    ],
)
origens = [
    item.strip()
    for item in os.getenv(
        "CORS_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500"
    ).split(",")
    if item.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origens,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(IntegrityError)
async def erro_integridade(request, exc):
    # Devolve erro legível em CPF/e-mail duplicado ou vínculo inválido.
    """Devolve erro legível em CPF/e-mail duplicado ou vínculo inválido."""
    mensagens = {
        1062: "Já existe um cadastro com esse CPF, e-mail, nome ou descrição.",
        1451: "Não foi possível excluir: este registro possui agendamentos, estilos, tatuadores ou usuários vinculados.",
        1452: "O registro relacionado não existe. Confira os IDs de cliente, tatuador, senioridade ou estilo.",
    }
    return JSONResponse(
        status_code=409,
        content={
            "detail": mensagens.get(
                exc.errno,
                "Não foi possível salvar: confira os dados e seus relacionamentos.",
            )
        },
    )


@app.exception_handler(InterfaceError)
@app.exception_handler(OperationalError)
async def erro_conexao(request, exc):
    # Informa uma falha de conexão sem revelar as credenciais privadas do banco.
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Não foi possível conectar ao banco. Confira o MySQL e as configurações do arquivo .env."
        },
    )


@app.get(
    "/uploads/{nome_arquivo}",
    include_in_schema=False,
    dependencies=[Depends(verificar_token)],
)
def mostrar_desenho(nome_arquivo: str):
    # Entrega a miniatura pela URL das aulas, exigindo uma sessão autenticada.
    return agendamentos.obter_desenho(nome_arquivo)


@app.get("/", tags=["Início"])
def inicio():
    # Confirma que a API está ativa.
    """Confirma que a API está ativa."""
    return {"mensagem": "API do estúdio de tatuagem funcionando!"}


app.include_router(login.router, tags=["Login"])
app.include_router(
    usuarios.router,
    prefix="/usuarios",
    tags=["Usuários"],
    dependencies=[Depends(verificar_admin)],
)
app.include_router(
    clientes.router,
    prefix="/clientes",
    tags=["Clientes"],
    dependencies=[Depends(verificar_token)],
)
app.include_router(
    senioridade.router,
    prefix="/senioridade",
    tags=["Senioridade"],
    dependencies=[Depends(verificar_token)],
)
app.include_router(
    estilos.router,
    prefix="/estilos",
    tags=["Estilos"],
    dependencies=[Depends(verificar_token)],
)
app.include_router(
    tatuadores.router,
    prefix="/tatuadores",
    tags=["Tatuadores"],
    dependencies=[Depends(verificar_token)],
)
app.include_router(
    agendamentos.router,
    prefix="/agendamentos",
    tags=["Agendamentos"],
    dependencies=[Depends(verificar_token)],
)
