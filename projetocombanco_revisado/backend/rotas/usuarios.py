# ============================================================
# usuarios.py — cadastro de funcionários por administradores
# ============================================================
import bcrypt
from fastapi import APIRouter

from database import obter_conexao
from modelos import UsuarioCadastro

# Os valores das consultas são enviados separadamente nos marcadores %s.
# Isso mantém o SQL parametrizado e evita tratar a entrada como código SQL.
router = APIRouter()


@router.get("")
def listar_usuarios():
    # Lista contas sem expor hashes de senha.
    """Lista contas sem expor hashes de senha."""
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute("SELECT idusuario,nome,email,tipo FROM usuario ORDER BY nome")
            return cur.fetchall()
        finally:
            cur.close()


@router.post("", status_code=201)
def criar_usuario(dados: UsuarioCadastro):
    # Cria uma conta de equipe com a senha protegida por bcrypt.
    """Cria uma conta de equipe com a senha protegida por bcrypt."""
    # encode transforma texto em bytes; gensalt cria um salt aleatório para cada hash.
    # decode permite guardar o hash resultante na coluna VARCHAR, sem expor a senha.
    hash_senha = bcrypt.hashpw(dados.senha.encode(), bcrypt.gensalt()).decode()
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO usuario (nome,email,senha,tipo) VALUES (%s,%s,%s,%s)",
                (dados.nome, dados.email, hash_senha, dados.tipo),
            )
            novo_id = cur.lastrowid
            conn.commit()
        finally:
            cur.close()
    return {
        "idusuario": novo_id,
        "nome": dados.nome,
        "email": dados.email,
        "tipo": dados.tipo,
    }
