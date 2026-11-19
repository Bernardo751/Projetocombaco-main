# ============================================================
# modelos.py — validação dos dados recebidos pela API
# ============================================================
import re
from datetime import date, time
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class Modelo(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=False)

    @field_validator("*", mode="before")
    @classmethod
    def normalizar_texto(cls, valor, info: ValidationInfo):
        # Remove espaços externos dos campos de texto sem modificar a senha.
        if info.field_name != "senha" and isinstance(valor, str):
            return valor.strip()
        return valor


class ClienteEntrada(Modelo):
    nome: str = Field(min_length=2, max_length=100)
    cpf: str = Field(pattern=r"^\d{11}$")
    telefone: Optional[str] = Field(default=None, max_length=20)
    datacadastro: Optional[date] = None
    cidade: Optional[str] = Field(default=None, max_length=100)
    uf: Optional[str] = Field(default=None, pattern=r"^[A-Za-z]{2}$")

    @field_validator("uf")
    @classmethod
    def normalizar_uf(cls, valor):
        # Converte a sigla do estado para letras maiúsculas.
        return valor.upper() if valor else valor


class SenioridadeEntrada(Modelo):
    nome: str = Field(min_length=2, max_length=50)


class EstiloEntrada(Modelo):
    descricao: str = Field(min_length=2, max_length=50)


class TatuadorEntrada(Modelo):
    nometatuador: str = Field(min_length=2, max_length=100)
    cpf: str = Field(pattern=r"^\d{11}$")
    email: Optional[str] = Field(default=None, max_length=100)
    telefone: Optional[str] = Field(default=None, max_length=20)
    datacontratacao: Optional[date] = None
    idsenioridade: int = Field(gt=0)


class AgendamentoEntrada(Modelo):
    idcliente: int = Field(gt=0)
    idtatuador: int = Field(gt=0)
    dataagendamento: date
    horaagendamento: time
    descricaotatuagem: Optional[str] = None
    valortatuagem: Optional[Decimal] = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )


class AgendamentoAtualizacao(AgendamentoEntrada):
    status: str = Field(pattern=r"^(pendente|confirmado|concluido|cancelado)$")


class UsuarioCadastro(Modelo):
    nome: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=150)
    senha: str = Field(min_length=10, max_length=72)
    tipo: str = Field(default="funcionario", pattern=r"^(funcionario|admin)$")

    @field_validator("email")
    @classmethod
    def validar_email(cls, valor):
        # Valida o formato do e-mail e normaliza as letras.
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valor):
            raise ValueError("Informe um e-mail válido")
        return valor.lower()

    @field_validator("senha")
    @classmethod
    def validar_tamanho_bcrypt(cls, valor):
        # Confere o limite de 72 bytes aceito pelo bcrypt.
        if len(valor.encode("utf-8")) > 72:
            raise ValueError("A senha deve ter no máximo 72 bytes")
        return valor


class LoginEntrada(Modelo):
    email: str = Field(min_length=5, max_length=150)
    senha: str = Field(min_length=1, max_length=72)

    @field_validator("senha")
    @classmethod
    def validar_senha_login(cls, valor):
        # Impede que senhas acima do limite do bcrypt causem erro interno no login.
        if len(valor.encode("utf-8")) > 72:
            raise ValueError("A senha deve ter no máximo 72 bytes")
        return valor


class EstilosTatuadorEntrada(Modelo):
    idestilos: list[int] = Field(max_length=100)
