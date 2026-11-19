# ============================================================
# login.py — autenticação de usuários com JWT
# ============================================================
import bcrypt
from fastapi import APIRouter, HTTPException

from database import obter_conexao
from modelos import LoginEntrada
from seguranca import criar_token

# Os valores das consultas são enviados separadamente nos marcadores %s.
# Isso mantém o SQL parametrizado e evita tratar a entrada como código SQL.
router = APIRouter()


@router.post("/login")
def login(dados: LoginEntrada):
    # Confere e-mail e senha e devolve um token de acesso.
    """Confere e-mail e senha e devolve um token de acesso."""
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute(
                "SELECT idusuario,email,senha,tipo FROM usuario WHERE email=%s",
                (dados.email.lower(),),
            )
            usuario = cur.fetchone()
        finally:
            cur.close()
    if not usuario or not bcrypt.checkpw(
        dados.senha.encode(), usuario["senha"].encode()
    ):
        raise HTTPException(401, "E-mail ou senha inválidos")
    token = criar_token(usuario["idusuario"], usuario["email"], usuario["tipo"])
    return {"access_token": token, "token_type": "bearer", "tipo": usuario["tipo"]}
