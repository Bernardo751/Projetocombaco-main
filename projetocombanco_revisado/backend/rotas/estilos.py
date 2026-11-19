# ============================================================
# estilos.py — catálogo de estilos e relação com tatuadores
# ============================================================
from fastapi import APIRouter, HTTPException
from database import obter_conexao
from modelos import EstiloEntrada

# Os valores das consultas são enviados separadamente nos marcadores %s.
# Isso mantém o SQL parametrizado e evita tratar a entrada como código SQL.
router = APIRouter()


@router.get("")
def listar_estilos():
    # Lista estilos cadastrados.
    """Lista estilos cadastrados."""
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute("SELECT * FROM estilo ORDER BY descricao")
            return cur.fetchall()
        finally:
            cur.close()


@router.get("/{id}")
def buscar_estilo(id: int):
    # Busca um estilo pelo ID.
    """Busca um estilo pelo ID."""
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute("SELECT * FROM estilo WHERE idestilo=%s", (id,))
            item = cur.fetchone()
        finally:
            cur.close()
    if not item:
        raise HTTPException(404, "Estilo não encontrado")
    return item


@router.post("", status_code=201)
def criar_estilo(dados: EstiloEntrada):
    # Cadastra um estilo de tatuagem.
    """Cadastra um estilo de tatuagem."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO estilo (descricao) VALUES (%s)", (dados.descricao,)
            )
            novo_id = cur.lastrowid
            conn.commit()
        finally:
            cur.close()
    return {"idestilo": novo_id, "descricao": dados.descricao}


@router.put("/{id}")
def atualizar_estilo(id: int, dados: EstiloEntrada):
    # Atualiza a descrição de um estilo.
    """Atualiza a descrição de um estilo."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE estilo SET descricao=%s WHERE idestilo=%s",
                (dados.descricao, id),
            )
            if cur.rowcount == 0:
                cur.execute("SELECT idestilo FROM estilo WHERE idestilo=%s", (id,))
                if not cur.fetchone():
                    raise HTTPException(404, "Estilo não encontrado")
            conn.commit()
        finally:
            cur.close()
    return {"mensagem": "Estilo atualizado"}


@router.delete("/{id}", status_code=204)
def excluir_estilo(id: int):
    # Exclui um estilo sem vínculos com tatuadores.
    """Exclui um estilo sem vínculos com tatuadores."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM estilo WHERE idestilo=%s", (id,))
            if cur.rowcount == 0:
                raise HTTPException(404, "Estilo não encontrado")
            conn.commit()
        finally:
            cur.close()
