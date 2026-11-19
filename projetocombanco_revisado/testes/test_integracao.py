# ============================================================
# test_integracao.py — testes reais da API com banco MySQL/MariaDB isolado
# Como rodar: leia VALIDACAO.md antes de habilitar o banco de testes.
# ============================================================
import base64
import os
from pathlib import Path
import secrets
import sys
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import mysql.connector
import pytest
from fastapi.testclient import TestClient

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))
RECURSOS = ["clientes", "senioridade", "estilos", "tatuadores", "agendamentos"]


@pytest.fixture(scope="session", autouse=True)
def banco_isolado():
    # Cria somente um banco de teste explicitamente habilitado e termina removendo-o.
    if os.getenv("EXECUTAR_TESTES_BANCO") != "1":
        pytest.skip("Habilite EXECUTAR_TESTES_BANCO=1 conforme VALIDACAO.md")
    nome = os.getenv("DB_NAME", "")
    if not nome.endswith("_teste") or not nome.replace("_", "").isalnum():
        pytest.fail(
            "Por segurança, DB_NAME deve terminar em _teste e conter só letras, números e _. Use um banco exclusivo."
        )
    os.environ.setdefault("SECRET_KEY", secrets.token_hex(32))
    configuracao = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
    }
    conexao = mysql.connector.connect(**configuracao)
    cursor = conexao.cursor()
    cursor.execute(
        f"CREATE DATABASE `{nome}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
    )
    # O CREATE falha se o banco já existir, evitando apagar dados anteriores por engano.
    try:
        texto = (
            (RAIZ / "banco/estudio_tatuagem.sql")
            .read_text()
            .replace("estudio_tatuagem", nome)
        )
        for comando in texto.split(";"):
            if comando.strip():
                cursor.execute(comando)
        conexao.commit()
        yield configuracao
    finally:
        cursor.execute(f"DROP DATABASE `{nome}`")
        cursor.close()
        conexao.close()


@pytest.fixture(scope="session")
def contexto(banco_isolado):
    # Prepara uma conta temporária e o cliente HTTP sem usar credenciais do aluno.
    from main import app
    from database import conectar

    senha = secrets.token_urlsafe(18)
    email = "admin-revisao@example.invalid"
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO usuario (nome,email,senha,tipo) VALUES (%s,%s,%s,'admin')",
            (
                "Admin de teste",
                email,
                bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode(),
            ),
        )
        conexao.commit()
        cursor.close()
    with TestClient(app) as cliente:
        resposta = cliente.post("/login", json={"email": email, "senha": senha})
        assert resposta.status_code == 200
        token = resposta.json()["access_token"]
        yield cliente, {"Authorization": f"Bearer {token}"}, email, senha


def enviar(contexto, metodo, caminho, dados=None, status=200, **opcoes):
    # Executa uma chamada autenticada e confere o código HTTP esperado.
    cliente, headers, _, _ = contexto
    resposta = cliente.request(metodo, caminho, json=dados, headers=headers, **opcoes)
    assert resposta.status_code == status, (metodo, caminho, resposta.text)
    return resposta.json() if resposta.content else None


def cpf_aleatorio():
    # Gera um identificador fictício de onze números para dados descartáveis.
    return f"{secrets.randbelow(10**11):011d}"


def test_raiz_documentacao_e_contratos(contexto):
    # Confere o endpoint inicial, o Swagger e os métodos das rotas das aulas.
    cliente = contexto[0]
    assert "mensagem" in cliente.get("/").json()
    assert cliente.get("/docs").status_code == 200
    esquema = cliente.get("/openapi.json").json()
    assert [tag["name"] for tag in esquema["tags"]][:2] == ["Login", "Usuários"]
    for recurso in RECURSOS:
        assert {"get", "post"} <= esquema["paths"][f"/{recurso}"].keys()
        assert {"get", "put", "delete"} <= esquema["paths"][f"/{recurso}/{{id}}"].keys()
    assert "post" in esquema["paths"]["/agendamentos/{id}/desenho"]
    assert {"get", "put"} <= esquema["paths"]["/tatuadores/{id}/estilos"].keys()


@pytest.mark.parametrize("recurso", RECURSOS)
def test_bloqueio_sem_token(contexto, recurso):
    # Garante que os cinco grupos de negócio exigem autenticação no backend.
    assert contexto[0].get(f"/{recurso}").status_code == 401


@pytest.mark.parametrize("recurso", RECURSOS)
@pytest.mark.parametrize("metodo", ["GET", "DELETE"])
def test_id_inexistente(contexto, recurso, metodo):
    # Confere o tratamento de IDs ausentes sem responder sucesso indevido.
    enviar(contexto, metodo, f"/{recurso}/2147483647", status=404)


def test_tokens_invalidos_e_expirados(contexto):
    # Rejeita token falso, expirado e token sem data de expiração.
    cliente, _, email, _ = contexto
    payload = {
        "sub": email,
        "tipo": "admin",
        "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
    }
    tokens = [
        "texto-invalido",
        jwt.encode(payload, os.environ["SECRET_KEY"], algorithm="HS256"),
    ]
    payload.pop("exp")
    tokens.append(jwt.encode(payload, os.environ["SECRET_KEY"], algorithm="HS256"))
    for token in tokens:
        assert (
            cliente.get(
                "/clientes", headers={"Authorization": f"Bearer {token}"}
            ).status_code
            == 401
        )


def test_login_hash_e_autorizacao(contexto):
    # Valida hash de senha, JWT de duas horas, duplicidade e o bloqueio do funcionário.
    cliente, headers, email, senha = contexto
    token = cliente.post("/login", json={"email": email, "senha": senha}).json()[
        "access_token"
    ]
    payload = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=["HS256"])
    assert payload["sub"] == email and payload["tipo"] == "admin"
    assert payload["exp"] - payload["iat"] == 7200
    assert (
        cliente.post(
            "/login", json={"email": email, "senha": secrets.token_urlsafe(16)}
        ).status_code
        == 401
    )
    assert (
        cliente.post(
            "/login", json={"email": "ausente@example.invalid", "senha": senha}
        ).status_code
        == 401
    )
    assert (
        cliente.post("/login", json={"email": email, "senha": "x" * 73}).status_code
        == 422
    )
    assert (
        cliente.post("/login", json={"email": email, "senha": "á" * 40}).status_code
        == 422
    )
    dados = {
        "nome": "Equipe de teste",
        "email": "equipe-revisao@example.invalid",
        "senha": " " + secrets.token_urlsafe(16) + " ",
        "tipo": "funcionario",
    }
    assert cliente.post("/usuarios", json=dados).status_code == 401
    conta = enviar(contexto, "POST", "/usuarios", dados, status=201)
    assert "senha" not in conta
    enviar(contexto, "POST", "/usuarios", dados, status=409)
    from database import conectar

    with conectar() as conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT senha FROM usuario WHERE email=%s", (dados["email"],))
        hash_senha = cursor.fetchone()["senha"]
        assert hash_senha != dados["senha"] and bcrypt.checkpw(
            dados["senha"].encode(), hash_senha.encode()
        )
        cursor.close()
    resposta = cliente.post(
        "/login", json={"email": dados["email"], "senha": dados["senha"]}
    )
    assert resposta.status_code == 200
    comum = {"Authorization": f"Bearer {resposta.json()['access_token']}"}
    assert cliente.post("/usuarios", json=dados, headers=comum).status_code == 403
    assert cliente.get("/usuarios", headers=comum).status_code == 403
    assert cliente.get("/clientes", headers=comum).status_code == 200
    assert all("senha" not in item for item in enviar(contexto, "GET", "/usuarios"))


def test_cruds_relacionamentos_e_upload(contexto):
    # Executa os cinco CRUDs, JOINs, N:N e o ciclo completo do desenho aprovado.
    sufixo = secrets.token_hex(4)
    senioridade = enviar(
        contexto, "POST", "/senioridade", {"nome": f"Nível {sufixo}"}, status=201
    )["idsenioridade"]
    estilo = enviar(
        contexto, "POST", "/estilos", {"descricao": f"Estilo {sufixo}"}, status=201
    )["idestilo"]
    outro = enviar(
        contexto, "POST", "/estilos", {"descricao": f"Outro {sufixo}"}, status=201
    )["idestilo"]
    cliente = {
        "nome": "Cliente fictício",
        "cpf": cpf_aleatorio(),
        "datacadastro": "2024-01-15",
        "uf": "sp",
    }
    idcliente = enviar(contexto, "POST", "/clientes", cliente, status=201)["idcliente"]
    enviar(contexto, "POST", "/clientes", cliente, status=409)
    cliente["nome"] = "Cliente alterado"
    for tentativa in range(2):
        enviar(contexto, "PUT", f"/clientes/{idcliente}", cliente)
    assert enviar(contexto, "GET", f"/clientes/{idcliente}")["uf"] == "SP"
    tatuador = {
        "nometatuador": "Tatuador fictício",
        "cpf": cpf_aleatorio(),
        "idsenioridade": senioridade,
    }
    idtatuador = enviar(contexto, "POST", "/tatuadores", tatuador, status=201)[
        "idtatuador"
    ]
    enviar(contexto, "PUT", f"/tatuadores/{idtatuador}", tatuador)
    assert any(
        t["idtatuador"] == idtatuador and t["estilos"] is None
        for t in enviar(contexto, "GET", "/tatuadores")
    )
    enviar(
        contexto,
        "PUT",
        f"/tatuadores/{idtatuador}/estilos",
        {"idestilos": [estilo, outro]},
    )
    assert len(enviar(contexto, "GET", f"/tatuadores/{idtatuador}/estilos")) == 2
    # Uma FK inválida deve desfazer a transação, preservando os estilos anteriores.
    enviar(
        contexto,
        "PUT",
        f"/tatuadores/{idtatuador}/estilos",
        {"idestilos": [2147483647]},
        status=409,
    )
    assert len(enviar(contexto, "GET", f"/tatuadores/{idtatuador}/estilos")) == 2
    enviar(contexto, "DELETE", f"/estilos/{estilo}", status=409)
    enviar(contexto, "DELETE", f"/senioridade/{senioridade}", status=409)
    dados = {
        "idcliente": idcliente,
        "idtatuador": idtatuador,
        "dataagendamento": "2026-10-22",
        "horaagendamento": "16:00:30",
        "valortatuagem": 0,
    }
    idagendamento = enviar(contexto, "POST", "/agendamentos", dados, status=201)[
        "idagendamento"
    ]
    agendamento = enviar(contexto, "GET", f"/agendamentos/{idagendamento}")
    assert (
        agendamento["status"] == "pendente"
        and agendamento["horaagendamento"] == "16:00:30"
    )
    assert any(
        a["idagendamento"] == idagendamento
        and a["cliente"] == cliente["nome"]
        and a["tatuador"] == tatuador["nometatuador"]
        for a in enviar(contexto, "GET", "/agendamentos")
    )
    enviar(contexto, "DELETE", f"/clientes/{idcliente}", status=409)
    enviar(contexto, "DELETE", f"/tatuadores/{idtatuador}", status=409)
    png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII="
    )
    http, headers, _, _ = contexto
    resposta = http.post(
        f"/agendamentos/{idagendamento}/desenho",
        headers=headers,
        files={"arquivo": ("imagem.png", png, "image/png")},
    )
    assert resposta.status_code == 201
    nome = resposta.json()["arquivo"]
    assert http.get(f"/uploads/{nome}").status_code == 401
    assert http.get(f"/uploads/{nome}", headers=headers).content == png
    dados["status"] = "confirmado"
    enviar(contexto, "PUT", f"/agendamentos/{idagendamento}", dados)
    assert (
        enviar(contexto, "GET", f"/agendamentos/{idagendamento}")["desenhoaprovado"]
        == nome
    )
    assert (
        http.post(
            f"/agendamentos/{idagendamento}/desenho",
            headers=headers,
            files={"arquivo": ("falso.png", b"nao-e-imagem", "image/png")},
        ).status_code
        == 415
    )
    assert (
        http.post(
            f"/agendamentos/{idagendamento}/desenho",
            headers=headers,
            files={
                "arquivo": ("grande.png", png + b"x" * (5 * 1024 * 1024), "image/png")
            },
        ).status_code
        == 413
    )
    resposta = http.post(
        f"/agendamentos/{idagendamento}/desenho",
        headers=headers,
        files={"arquivo": ("nova.png", png, "image/png")},
    )
    assert resposta.status_code == 201
    novo_nome = resposta.json()["arquivo"]
    assert http.get(f"/uploads/{nome}", headers=headers).status_code == 404
    enviar(contexto, "DELETE", f"/agendamentos/{idagendamento}", status=204)
    assert http.get(f"/uploads/{novo_nome}", headers=headers).status_code == 404
    enviar(contexto, "PUT", f"/tatuadores/{idtatuador}/estilos", {"idestilos": []})
    assert enviar(contexto, "GET", f"/tatuadores/{idtatuador}/estilos") == []
    enviar(contexto, "DELETE", f"/tatuadores/{idtatuador}", status=204)
    enviar(contexto, "DELETE", f"/clientes/{idcliente}", status=204)
    enviar(
        contexto, "PUT", f"/senioridade/{senioridade}", {"nome": f"Alterado {sufixo}"}
    )
    assert (
        enviar(contexto, "GET", f"/senioridade/{senioridade}")["nome"]
        == f"Alterado {sufixo}"
    )
    enviar(contexto, "PUT", f"/estilos/{estilo}", {"descricao": f"Alterado {sufixo}"})
    assert (
        enviar(contexto, "GET", f"/estilos/{estilo}")["descricao"]
        == f"Alterado {sufixo}"
    )
    for recurso, id in [
        ("senioridade", senioridade),
        ("estilos", estilo),
        ("estilos", outro),
    ]:
        enviar(contexto, "DELETE", f"/{recurso}/{id}", status=204)


def test_validacoes_e_cors(contexto):
    # Confere mensagens estruturadas e a permissão de chamada das origens locais.
    cliente, headers, _, _ = contexto
    enviar(contexto, "POST", "/clientes", {"nome": "Ana", "cpf": "abc"}, status=422)
    enviar(contexto, "POST", "/agendamentos", {"idcliente": -1}, status=422)
    for origem in ["http://127.0.0.1:5500", "http://localhost:5500"]:
        resposta = cliente.options(
            "/clientes",
            headers={
                "Origin": origem,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )
        assert resposta.status_code == 200
        assert resposta.headers["access-control-allow-origin"] == origem
    resposta = cliente.get(
        "/clientes", headers={**headers, "Origin": "https://outro.example.invalid"}
    )
    assert "access-control-allow-origin" not in resposta.headers
