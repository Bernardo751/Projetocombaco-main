from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import conectar
import os

router = APIRouter()

# Pasta onde as imagens serão salvas
PASTA_UPLOADS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(PASTA_UPLOADS, exist_ok=True)


# Modelo de dados do agendamento
class Agendamento(BaseModel):
    idcliente: int
    idtatuador: int
    dataagendamento: str
    horaagendamento: str
    descricaotatuagem: Optional[str] = None
    valortatuagem: Optional[float] = None
    status: Optional[str] = None


# POST /agendamentos — cadastrar e devolver o ID criado
@router.post("/agendamentos")
def criar_agendamento(agendamento: Agendamento):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO agendamento (
                idcliente,
                idtatuador,
                dataagendamento,
                horaagendamento,
                descricaotatuagem,
                valortatuagem
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                agendamento.idcliente,
                agendamento.idtatuador,
                agendamento.dataagendamento,
                agendamento.horaagendamento,
                agendamento.descricaotatuagem,
                agendamento.valortatuagem
            )
        )

        novo_id = cursor.lastrowid
        conn.commit()

        return {
            "mensagem": "Agendamento cadastrado com sucesso",
            "idagendamento": novo_id
        }
    finally:
        cursor.close()
        conn.close()


# GET /agendamentos — listar todos
@router.get("/agendamentos")
def listar_agendamentos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                agendamento.*,
                cliente.nome AS cliente,
                tatuador.nometatuador AS tatuador
            FROM agendamento
            JOIN cliente
                ON agendamento.idcliente = cliente.idcliente
            JOIN tatuador
                ON agendamento.idtatuador = tatuador.idtatuador
        """)

        agendamentos = cursor.fetchall()

        for a in agendamentos:
            hora = a["horaagendamento"]

            if hasattr(hora, "total_seconds"):
                total_segundos = int(hora.total_seconds())
                horas, resto = divmod(total_segundos, 3600)
                minutos, segundos = divmod(resto, 60)
                a["horaagendamento"] = (
                    f"{horas:02d}:{minutos:02d}:{segundos:02d}"
                )
            elif hora is not None:
                a["horaagendamento"] = str(hora)

        return agendamentos
    finally:
        cursor.close()
        conn.close()


# GET /agendamentos/{id} — buscar um agendamento
@router.get("/agendamentos/{id}")
def buscar_agendamento(id: int):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM agendamento WHERE idagendamento = %s",
            (id,)
        )
        agendamento = cursor.fetchone()

        if not agendamento:
            raise HTTPException(
                status_code=404,
                detail="Agendamento não encontrado"
            )

        hora = agendamento["horaagendamento"]

        if hasattr(hora, "total_seconds"):
            total_segundos = int(hora.total_seconds())
            horas, resto = divmod(total_segundos, 3600)
            minutos, segundos = divmod(resto, 60)
            agendamento["horaagendamento"] = (
                f"{horas:02d}:{minutos:02d}:{segundos:02d}"
            )
        elif hora is not None:
            agendamento["horaagendamento"] = str(hora)

        return agendamento
    finally:
        cursor.close()
        conn.close()


# PUT /agendamentos/{id} — atualizar um agendamento
@router.put("/agendamentos/{id}")
def atualizar_agendamento(id: int, agendamento: Agendamento):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE agendamento
            SET idcliente = %s,
                idtatuador = %s,
                dataagendamento = %s,
                horaagendamento = %s,
                descricaotatuagem = %s,
                valortatuagem = %s,
                status = %s
            WHERE idagendamento = %s
            """,
            (
                agendamento.idcliente,
                agendamento.idtatuador,
                agendamento.dataagendamento,
                agendamento.horaagendamento,
                agendamento.descricaotatuagem,
                agendamento.valortatuagem,
                agendamento.status,
                id
            )
        )

        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT idagendamento FROM agendamento WHERE idagendamento = %s",
                (id,)
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Agendamento não encontrado"
                )

        conn.commit()

        return {"mensagem": "Agendamento atualizado com sucesso"}
    finally:
        cursor.close()
        conn.close()


# DELETE /agendamentos/{id} — excluir um agendamento
@router.delete("/agendamentos/{id}")
def deletar_agendamento(id: int):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM agendamento WHERE idagendamento = %s",
            (id,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Agendamento não encontrado"
            )

        conn.commit()

        return {"mensagem": "Agendamento deletado com sucesso"}
    finally:
        cursor.close()
        conn.close()


# POST /agendamentos/{id}/desenho — enviar desenho aprovado
@router.post("/agendamentos/{id}/desenho")
async def upload_desenho(
    id: int,
    arquivo: UploadFile = File(...)
):
    if not arquivo.filename:
        raise HTTPException(
            status_code=400,
            detail="Nenhum arquivo foi selecionado"
        )

    extensao = os.path.splitext(arquivo.filename)[1].lower()
    extensoes_permitidas = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

    if extensao not in extensoes_permitidas:
        raise HTTPException(
            status_code=400,
            detail="Formato inválido. Envie JPG, PNG, WEBP ou GIF."
        )

    conteudo = await arquivo.read()

    if not conteudo:
        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado está vazio"
        )

    if len(conteudo) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="A imagem deve ter no máximo 5 MB"
        )

    nome_original = os.path.basename(arquivo.filename)
    nome_arquivo = f"{id}_{nome_original}"
    caminho = os.path.join(PASTA_UPLOADS, nome_arquivo)

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT idagendamento FROM agendamento WHERE idagendamento = %s",
            (id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Agendamento não encontrado"
            )

        # Salva a imagem na pasta uploads
        with open(caminho, "wb") as f:
            f.write(conteudo)

        # Salva o nome da imagem no banco
        cursor.execute(
            """
            UPDATE agendamento
            SET desenhoaprovado = %s
            WHERE idagendamento = %s
            """,
            (nome_arquivo, id)
        )

        conn.commit()

        return {
            "mensagem": "Desenho enviado com sucesso",
            "arquivo": nome_arquivo
        }
    finally:
        cursor.close()
        conn.close()
        await arquivo.close()