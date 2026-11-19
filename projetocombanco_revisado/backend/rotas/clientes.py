# ============================================================
# clientes.py — operações de clientes
# ============================================================
from fastapi import APIRouter, HTTPException, status
from database import obter_conexao
from modelos import ClienteEntrada

# Os valores das consultas são enviados separadamente nos marcadores %s.
# Isso mantém o SQL parametrizado e evita tratar a entrada como código SQL.
router = APIRouter()


@router.get("")
def listar_clientes():
    # Lista clientes em ordem alfabética.
    """Lista clientes em ordem alfabética."""
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute("SELECT * FROM cliente ORDER BY nome")
            return cur.fetchall()
        finally:
            cur.close()


@router.get("/{id}")
def buscar_cliente(id: int):
    # Busca um cliente pelo identificador.
    """Busca um cliente pelo identificador."""
    with obter_conexao() as conn:
        cur = conn.cursor(dictionary=True)  # Cada linha do SELECT vira um dicionário.
        try:
            cur.execute("SELECT * FROM cliente WHERE idcliente=%s", (id,))
            item = cur.fetchone()
        finally:
            cur.close()
    if not item:
        raise HTTPException(404, "Cliente não encontrado")
    return item


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_cliente(dados: ClienteEntrada):
    # Cadastra um cliente e devolve o ID criado.
    """Cadastra um cliente e devolve o ID criado."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO cliente (nome,cpf,telefone,datacadastro,cidade,uf) VALUES (%s,%s,%s,%s,%s,%s)",
                (
                    dados.nome,
                    dados.cpf,
                    dados.telefone,
                    dados.datacadastro,
                    dados.cidade,
                    dados.uf,
                ),
            )
            novo_id = cur.lastrowid
            conn.commit()
        finally:
            cur.close()
    return {"mensagem": "Cliente cadastrado", "idcliente": novo_id}


@router.put("/{id}")
def atualizar_cliente(id: int, dados: ClienteEntrada):
    # Atualiza os dados de um cliente existente.
    """Atualiza os dados de um cliente existente."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE cliente SET nome=%s,cpf=%s,telefone=%s,datacadastro=%s,cidade=%s,uf=%s WHERE idcliente=%s",
                (
                    dados.nome,
                    dados.cpf,
                    dados.telefone,
                    dados.datacadastro,
                    dados.cidade,
                    dados.uf,
                    id,
                ),
            )
            if cur.rowcount == 0:
                cur.execute("SELECT idcliente FROM cliente WHERE idcliente=%s", (id,))
                if not cur.fetchone():
                    raise HTTPException(404, "Cliente não encontrado")
            conn.commit()
        finally:
            cur.close()
    return {"mensagem": "Cliente atualizado"}


@router.delete("/{id}", status_code=204)
def excluir_cliente(id: int):
    # Exclui cliente sem agendamentos vinculados.
    """Exclui cliente sem agendamentos vinculados."""
    with obter_conexao() as conn:
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM cliente WHERE idcliente=%s", (id,))
            if cur.rowcount == 0:
                raise HTTPException(404, "Cliente não encontrado")
            conn.commit()
        finally:
            cur.close()
