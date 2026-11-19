# ============================================================
# senioridade.py — níveis profissionais dos tatuadores
# ============================================================
from fastapi import APIRouter, HTTPException
from database import obter_conexao
from modelos import SenioridadeEntrada

# Os valores das consultas são enviados separadamente nos marcadores %s.
# Isso mantém o SQL parametrizado e evita tratar a entrada como código SQL.
router = APIRouter()


@router.get("")
def listar_senioridades():
    # Lista os níveis de senioridade.
    """Lista os níveis de senioridade."""
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute("SELECT * FROM senioridade ORDER BY idsenioridade")
            return cur.fetchall()
        finally:
            cur.close()


@router.get("/{id}")
def buscar_senioridade(id: int):
    # Busca um nível pelo ID.
    """Busca um nível pelo ID."""
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute("SELECT * FROM senioridade WHERE idsenioridade=%s", (id,))
            item = cur.fetchone()
        finally:
            cur.close()
    if not item:
        raise HTTPException(404, "Senioridade não encontrada")
    return item


@router.post("", status_code=201)
def criar_senioridade(dados: SenioridadeEntrada):
    # Cria um nível profissional.
    """Cria um nível profissional."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO senioridade (nome) VALUES (%s)", (dados.nome,))
            novo_id = cur.lastrowid
            conn.commit()
        finally:
            cur.close()
    return {"idsenioridade": novo_id, "nome": dados.nome}


@router.put("/{id}")
def atualizar_senioridade(id: int, dados: SenioridadeEntrada):
    # Atualiza o nome de um nível.
    """Atualiza o nome de um nível."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE senioridade SET nome=%s WHERE idsenioridade=%s",
                (dados.nome, id),
            )
            if cur.rowcount == 0:
                cur.execute(
                    "SELECT idsenioridade FROM senioridade WHERE idsenioridade=%s",
                    (id,),
                )
                if not cur.fetchone():
                    raise HTTPException(404, "Senioridade não encontrada")
            conn.commit()
        finally:
            cur.close()
    return {"mensagem": "Senioridade atualizada"}


@router.delete("/{id}", status_code=204)
def excluir_senioridade(id: int):
    # Exclui um nível que não esteja associado a tatuadores.
    """Exclui um nível que não esteja associado a tatuadores."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM senioridade WHERE idsenioridade=%s", (id,))
            if cur.rowcount == 0:
                raise HTTPException(404, "Senioridade não encontrada")
            conn.commit()
        finally:
            cur.close()
