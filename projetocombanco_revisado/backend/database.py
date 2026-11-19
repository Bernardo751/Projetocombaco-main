# ============================================================
# database.py — conexão com o banco MySQL do estúdio
# ============================================================
import os
from contextlib import contextmanager

import mysql.connector
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


def conectar():
    # Abre uma conexão usando as configurações privadas do .env.
    """Abre uma conexão usando as configurações privadas do .env."""
    # As credenciais vêm do .env; a porta também atende serviços remotos como o Aiven.
    configuracao = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "estudio_tatuagem"),
    }
    certificado = os.getenv("DB_SSL_CA")
    if certificado:
        # O certificado CA valida o servidor e o nome do host durante a conexão TLS.
        configuracao.update(
            ssl_ca=certificado, ssl_verify_cert=True, ssl_verify_identity=True
        )
    return mysql.connector.connect(**configuracao)


@contextmanager
def obter_conexao():
    # Garante que a conexão seja fechada mesmo quando uma consulta falha.
    """Garante que a conexão seja fechada mesmo quando uma consulta falha."""
    conexao = conectar()
    try:
        yield conexao  # Entrega a conexão ao bloco with que executa a consulta.
    except Exception:
        conexao.rollback()  # Desfaz gravações parciais antes de propagar a falha.
        raise
    finally:
        conexao.close()
