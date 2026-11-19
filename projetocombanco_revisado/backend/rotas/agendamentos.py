# ============================================================
# agendamentos.py — CRUD de sessões e upload de desenhos
# ============================================================
import os
import re
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from database import obter_conexao
from modelos import AgendamentoAtualizacao, AgendamentoEntrada
from seguranca import verificar_token

# Os valores das consultas são enviados separadamente nos marcadores %s.
# Isso mantém o SQL parametrizado e evita tratar a entrada como código SQL.
router = APIRouter()
UPLOADS = Path(__file__).resolve().parents[1] / "uploads"
UPLOADS.mkdir(parents=True, exist_ok=True)
MAX_UPLOAD = int(os.getenv("MAX_UPLOAD_MB", "5")) * 1024 * 1024
TIPOS_IMAGEM = {
    "image/jpeg": (".jpg", lambda dados: dados.startswith(b"\xff\xd8\xff")),
    "image/png": (".png", lambda dados: dados.startswith(b"\x89PNG\r\n\x1a\n")),
    "image/webp": (
        ".webp",
        lambda dados: dados[:4] == b"RIFF" and dados[8:12] == b"WEBP",
    ),
}


@router.get("")
def listar_agendamentos():
    # Lista agendamentos com os nomes do cliente e do tatuador.
    """Lista agendamentos com os nomes do cliente e do tatuador."""
    # Os JOINs trazem os nomes; TIME_FORMAT transforma TIME em texto HH:MM:SS.
    # %S significa segundos sem se confundir com o marcador de parâmetro %s.
    consulta = """
        SELECT a.*, DATE_FORMAT(a.dataagendamento, '%Y-%m-%d') AS dataagendamento,
               TIME_FORMAT(a.horaagendamento, '%H:%i:%S') AS horaagendamento,
               c.nome AS cliente, t.nometatuador AS tatuador
        FROM agendamento a JOIN cliente c ON c.idcliente=a.idcliente
        JOIN tatuador t ON t.idtatuador=a.idtatuador
        ORDER BY a.dataagendamento, a.horaagendamento
    """
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute(consulta)
            return cur.fetchall()
        finally:
            cur.close()


@router.get("/{id}")
def buscar_agendamento(id: int):
    # Busca um agendamento pelo ID.
    """Busca um agendamento pelo ID."""
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute(
                "SELECT *,DATE_FORMAT(dataagendamento,'%Y-%m-%d') AS dataagendamento,TIME_FORMAT(horaagendamento,'%H:%i:%S') AS horaagendamento FROM agendamento WHERE idagendamento=%s",
                (id,),
            )
            item = cur.fetchone()
        finally:
            cur.close()
    if not item:
        raise HTTPException(404, "Agendamento não encontrado")
    return item


@router.post("", status_code=201)
def criar_agendamento(dados: AgendamentoEntrada):
    # Cria um agendamento com status pendente.
    """Cria um agendamento com status pendente."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO agendamento (idcliente,idtatuador,dataagendamento,horaagendamento,descricaotatuagem,valortatuagem) VALUES (%s,%s,%s,%s,%s,%s)",
                (
                    dados.idcliente,
                    dados.idtatuador,
                    dados.dataagendamento,
                    dados.horaagendamento,
                    dados.descricaotatuagem,
                    dados.valortatuagem,
                ),
            )
            novo_id = cur.lastrowid
            conn.commit()
        finally:
            cur.close()
    return {
        "idagendamento": novo_id,
        "mensagem": "Agendamento criado",
        "status": "pendente",
    }


@router.put("/{id}")
def atualizar_agendamento(id: int, dados: AgendamentoAtualizacao):
    # Atualiza os dados e o status de um agendamento.
    """Atualiza os dados e o status de um agendamento."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE agendamento SET idcliente=%s,idtatuador=%s,dataagendamento=%s,horaagendamento=%s,descricaotatuagem=%s,valortatuagem=%s,status=%s WHERE idagendamento=%s",
                (
                    dados.idcliente,
                    dados.idtatuador,
                    dados.dataagendamento,
                    dados.horaagendamento,
                    dados.descricaotatuagem,
                    dados.valortatuagem,
                    dados.status,
                    id,
                ),
            )
            if cur.rowcount == 0:
                cur.execute(
                    "SELECT idagendamento FROM agendamento WHERE idagendamento=%s",
                    (id,),
                )
                if not cur.fetchone():
                    raise HTTPException(404, "Agendamento não encontrado")
            conn.commit()
        finally:
            cur.close()
    return {"mensagem": "Agendamento atualizado"}


@router.delete("/{id}", status_code=204)
def excluir_agendamento(id: int):
    # Exclui um agendamento e o desenho associado, se houver.
    """Exclui um agendamento e o desenho associado, se houver."""
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute(
                "SELECT desenhoaprovado FROM agendamento WHERE idagendamento=%s", (id,)
            )
            item = cur.fetchone()
            if not item:
                raise HTTPException(404, "Agendamento não encontrado")
            cur.execute("DELETE FROM agendamento WHERE idagendamento=%s", (id,))
            conn.commit()
        finally:
            cur.close()
    if item["desenhoaprovado"]:
        (UPLOADS / item["desenhoaprovado"]).unlink(missing_ok=True)


@router.post("/{id}/desenho", status_code=201)
async def enviar_desenho(id: int, arquivo: UploadFile = File(...)):
    # Valida e associa uma imagem pequena ao agendamento.
    """Valida e associa uma imagem pequena ao agendamento."""
    conteudo = await arquivo.read(MAX_UPLOAD + 1)
    await arquivo.close()
    if len(conteudo) > MAX_UPLOAD:
        raise HTTPException(
            413, f"A imagem deve ter no máximo {MAX_UPLOAD // (1024 * 1024)} MB"
        )
    tipo = TIPOS_IMAGEM.get(arquivo.content_type or "")
    if not tipo or not tipo[1](conteudo):
        raise HTTPException(415, "Envie uma imagem JPG, PNG ou WEBP válida")
    nome = f"{uuid.uuid4().hex}{tipo[0]}"
    destino = UPLOADS / nome
    imagem_anterior = None
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute(
                "SELECT idagendamento,desenhoaprovado FROM agendamento WHERE idagendamento=%s",
                (id,),
            )
            agendamento = cur.fetchone()
            if not agendamento:
                raise HTTPException(404, "Agendamento não encontrado")
            imagem_anterior = agendamento["desenhoaprovado"]
            destino.write_bytes(conteudo)
            cur.execute(
                "UPDATE agendamento SET desenhoaprovado=%s WHERE idagendamento=%s",
                (nome, id),
            )
            conn.commit()
        except Exception:
            destino.unlink(missing_ok=True)
            raise
        finally:
            cur.close()
    if imagem_anterior:
        (UPLOADS / imagem_anterior).unlink(missing_ok=True)
    return {"mensagem": "Imagem enviada", "arquivo": nome}


@router.get("/arquivos/{filename}", include_in_schema=False)
def obter_desenho(filename: str, usuario=Depends(verificar_token)):
    # Entrega a imagem somente a uma pessoa autenticada.
    """Entrega a imagem somente a uma pessoa autenticada."""
    if not re.fullmatch(r"[\w .-]+\.(jpg|jpeg|png|webp)", filename, re.IGNORECASE):
        raise HTTPException(404, "Imagem não encontrada")
    caminho = (UPLOADS / filename).resolve()
    if caminho.parent != UPLOADS.resolve():
        raise HTTPException(404, "Imagem não encontrada")
    if not caminho.is_file():
        raise HTTPException(404, "Imagem não encontrada")
    return FileResponse(caminho)
