# ============================================================
# seguranca.py — autenticação JWT e autorização de administrador
# ============================================================
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database import obter_conexao

ESQUEMA_TOKEN = HTTPBearer(auto_error=False)
ALGORITMO = "HS256"


def _chave_secreta():
    # Lê a chave privada de assinatura e exige um tamanho mínimo.
    chave = os.getenv("SECRET_KEY")
    if not chave or len(chave) < 32:
        raise RuntimeError(
            "Configure SECRET_KEY com pelo menos 32 caracteres no arquivo .env"
        )
    return chave


def criar_token(usuario_id: int, email: str, tipo: str) -> str:
    # Assina um JWT com validade de duas horas.
    """Assina um JWT com validade de duas horas."""
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "idusuario": str(usuario_id),
        "email": email,
        "tipo": tipo,
        "iat": agora,
        "exp": agora + timedelta(hours=2),
    }
    return jwt.encode(payload, _chave_secreta(), algorithm=ALGORITMO)


def verificar_token(
    credenciais: HTTPAuthorizationCredentials | None = Depends(ESQUEMA_TOKEN),
):
    # Valida o token e consulta a existência e o tipo atual da conta no banco.
    """Valida o token e consulta a existência e o tipo atual da conta no banco."""
    if credenciais is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Faça login para continuar"
        )
    try:
        dados = jwt.decode(
            credenciais.credentials,
            _chave_secreta(),
            algorithms=[ALGORITMO],
            options={"require": ["sub", "tipo", "exp"]},
        )
        # O campo email também permite aceitar tokens da versão anterior até expirarem.
        email = dados.get("email", dados["sub"])
        if not isinstance(email, str) or "@" not in email:
            raise ValueError("Identificação inválida")
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    with obter_conexao() as conexao:
        cursor = conexao.cursor(dictionary=True)  # Retorna colunas por nome.
        try:
            cursor.execute(
                "SELECT idusuario, email, tipo FROM usuario WHERE email = %s", (email,)
            )
            usuario = cursor.fetchone()
        finally:
            cursor.close()
    if not usuario:
        raise HTTPException(status_code=401, detail="Conta não encontrada")
    return usuario


def verificar_admin(usuario=Depends(verificar_token)):
    # Permite a ação somente para uma conta que atualmente seja administradora.
    """Permite a ação somente para uma conta que atualmente seja administradora."""
    if usuario["tipo"] != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return usuario
