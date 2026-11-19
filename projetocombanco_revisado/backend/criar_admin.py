# ============================================================
# criar_admin.py — cria a conta inicial de administrador
# Execute uma vez com: python criar_admin.py
# ============================================================
import getpass
import bcrypt
from pydantic import ValidationError
from mysql.connector import Error

from database import obter_conexao
from modelos import UsuarioCadastro


def criar_administrador():
    # Solicita credenciais no terminal e cria a conta inicial com bcrypt.
    """Solicita credenciais no terminal e cria a conta inicial com bcrypt."""
    nome = input("Nome do administrador: ").strip()
    email = input("E-mail do administrador: ").strip().lower()
    senha = getpass.getpass("Senha (mínimo 10 caracteres): ")
    try:
        dados = UsuarioCadastro(nome=nome, email=email, senha=senha, tipo="admin")
    except ValidationError as erro:
        raise SystemExit(
            "Dados inválidos: " + "; ".join(item["msg"] for item in erro.errors())
        )
    nome, email, senha = dados.nome, dados.email, dados.senha
    hash_senha = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO usuario (nome,email,senha,tipo) VALUES (%s,%s,%s,'admin')",
                (nome, email, hash_senha),
            )
            conn.commit()
        finally:
            cur.close()
    print("Administrador criado. Faça login pela tela do sistema.")


if __name__ == "__main__":
    try:
        criar_administrador()
    except Error as erro:
        if erro.errno == 1062:
            raise SystemExit(
                "Este e-mail já está cadastrado. Entre com a conta existente."
            )
        raise SystemExit(
            "Não foi possível criar o administrador. Confira o MySQL, a importação do banco e o arquivo .env."
        )
