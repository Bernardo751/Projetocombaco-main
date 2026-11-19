# ============================================================
# tatuadores.py — CRUD de tatuadores e seus estilos
# ============================================================
from fastapi import APIRouter, HTTPException
from database import obter_conexao
from modelos import EstilosTatuadorEntrada, TatuadorEntrada

# Os valores das consultas são enviados separadamente nos marcadores %s.
# Isso mantém o SQL parametrizado e evita tratar a entrada como código SQL.
router = APIRouter()


@router.get("")
def listar_tatuadores():
    # Lista tatuadores com senioridade e estilos associados.
    """Lista tatuadores com senioridade e estilos associados."""
    # GROUP_CONCAT reúne os estilos; LEFT JOIN mantém quem ainda não tem nenhum.
    # A subconsulta agrupa só o vínculo, evitando conflito com ONLY_FULL_GROUP_BY.
    consulta = """
        SELECT t.*, s.nome AS senioridade, e.estilos
        FROM tatuador t
        JOIN senioridade s ON s.idsenioridade=t.idsenioridade
        LEFT JOIN (
            SELECT te.idtatuador, GROUP_CONCAT(es.descricao ORDER BY es.descricao SEPARATOR ', ') AS estilos
            FROM tatuador_estilo te JOIN estilo es ON es.idestilo=te.idestilo
            GROUP BY te.idtatuador
        ) e ON e.idtatuador=t.idtatuador
        ORDER BY t.nometatuador
    """
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute(consulta)
            return cur.fetchall()
        finally:
            cur.close()


@router.get("/{id}")
def buscar_tatuador(id: int):
    # Busca um tatuador pelo ID.
    """Busca um tatuador pelo ID."""
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute("SELECT * FROM tatuador WHERE idtatuador=%s", (id,))
            item = cur.fetchone()
        finally:
            cur.close()
    if not item:
        raise HTTPException(404, "Tatuador não encontrado")
    return item


@router.post("", status_code=201)
def criar_tatuador(dados: TatuadorEntrada):
    # Cadastra um tatuador e devolve o ID criado.
    """Cadastra um tatuador e devolve o ID criado."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO tatuador (nometatuador,cpf,email,telefone,datacontratacao,idsenioridade) VALUES (%s,%s,%s,%s,%s,%s)",
                (
                    dados.nometatuador,
                    dados.cpf,
                    dados.email,
                    dados.telefone,
                    dados.datacontratacao,
                    dados.idsenioridade,
                ),
            )
            novo_id = cur.lastrowid
            conn.commit()
        finally:
            cur.close()
    return {"idtatuador": novo_id, "mensagem": "Tatuador cadastrado"}


@router.put("/{id}")
def atualizar_tatuador(id: int, dados: TatuadorEntrada):
    # Atualiza os dados de um tatuador.
    """Atualiza os dados de um tatuador."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE tatuador SET nometatuador=%s,cpf=%s,email=%s,telefone=%s,datacontratacao=%s,idsenioridade=%s WHERE idtatuador=%s",
                (
                    dados.nometatuador,
                    dados.cpf,
                    dados.email,
                    dados.telefone,
                    dados.datacontratacao,
                    dados.idsenioridade,
                    id,
                ),
            )
            if cur.rowcount == 0:
                cur.execute(
                    "SELECT idtatuador FROM tatuador WHERE idtatuador=%s", (id,)
                )
                if not cur.fetchone():
                    raise HTTPException(404, "Tatuador não encontrado")
            conn.commit()
        finally:
            cur.close()
    return {"mensagem": "Tatuador atualizado"}


@router.delete("/{id}", status_code=204)
def excluir_tatuador(id: int):
    # Exclui um tatuador sem agendamentos vinculados.
    """Exclui um tatuador sem agendamentos vinculados."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM tatuador WHERE idtatuador=%s", (id,))
            if cur.rowcount == 0:
                raise HTTPException(404, "Tatuador não encontrado")
            conn.commit()
        finally:
            cur.close()


@router.get("/{id}/estilos")
def listar_estilos(id: int):
    # Lista os estilos associados a um tatuador.
    """Lista os estilos associados a um tatuador."""
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute("SELECT idtatuador FROM tatuador WHERE idtatuador=%s", (id,))
            if not cur.fetchone():
                raise HTTPException(404, "Tatuador não encontrado")
            cur.execute(
                "SELECT e.idestilo,e.descricao FROM tatuador_estilo te JOIN estilo e ON e.idestilo=te.idestilo WHERE te.idtatuador=%s ORDER BY e.descricao",
                (id,),
            )
            return cur.fetchall()
        finally:
            cur.close()


@router.put("/{id}/estilos")
def atualizar_estilos(id: int, dados: EstilosTatuadorEntrada):
    # Substitui a lista de estilos de um tatuador em uma transação.
    """Substitui a lista de estilos de um tatuador em uma transação."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute("SELECT idtatuador FROM tatuador WHERE idtatuador=%s", (id,))
            if not cur.fetchone():
                raise HTTPException(404, "Tatuador não encontrado")
            cur.execute("DELETE FROM tatuador_estilo WHERE idtatuador=%s", (id,))
            for estilo_id in set(dados.idestilos):
                cur.execute(
                    "INSERT INTO tatuador_estilo (idtatuador,idestilo,dataestilo) VALUES (%s,%s,CURDATE())",
                    (id, estilo_id),
                )
            conn.commit()
        finally:
            cur.close()
    return {"mensagem": "Estilos atualizados"}
