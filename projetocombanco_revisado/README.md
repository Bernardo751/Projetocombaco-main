# Estúdio de Tatuagem — projeto revisado

Implementação baseada nas 17 aulas de [Cíntia Pinho](https://github.com/cintiapinho/projetocombanco), com MySQL/MariaDB, Python/FastAPI, HTML, Bootstrap e JavaScript/Fetch.

**Se você já usa a solução anterior e criou seu administrador, comece por [ATUALIZACAO.md](ATUALIZACAO.md).** Não é necessário criar essa conta novamente.

O que foi conferido e o que ainda depende do seu ambiente estão em [REVISAO_DAS_17_AULAS.md](REVISAO_DAS_17_AULAS.md). A revisão não significa aprovação da professora. A hospedagem real no Aiven continua pendente até você configurar e testar o serviço remoto.

## Instalação inicial no Windows

1. Ligue Apache e MySQL no XAMPP. Pelo phpMyAdmin, importe `banco/estudio_tatuagem.sql`. Ele cria as sete tabelas finais e os catálogos de senioridade/estilos. Se quiser reproduzir os exemplos da aula 2 em um banco de estudo, importe também `banco/dados_exemplo.sql`.
2. Abra o CMD dentro de `backend/`:

   ```cmd
   python -m venv venv
   venv\Scripts\activate.bat
   python -m pip install -r requirements.txt
   copy .env.example .env
   notepad .env
   ```

   No PowerShell, a ativação equivalente é `.\venv\Scripts\Activate.ps1`. Use o comando correspondente ao terminal que você abriu.

3. Ajuste as configurações do banco no `.env`. No XAMPP padrão: host `localhost`, porta `3306`, usuário `root`, senha vazia e banco `estudio_tatuagem`. Gere sua chave privada com:

   ```cmd
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

   Cole o resultado somente em `SECRET_KEY` no `.env`. Se uma chave real já foi compartilhada, substitua-a por uma nova e reinicie a API. O arquivo privado não acompanha o pacote.

4. Para a primeira instalação, crie a conta administrativa diretamente no banco e inicie a API:

   ```cmd
   python criar_admin.py
   python -m uvicorn main:app --reload
   ```

   Ao digitar a senha no terminal, nenhum caractere ou asterisco aparece. Digite pelo menos 10 caracteres, até 72 bytes, e pressione Enter. O script faz o mesmo hash/INSERT da aula 16, sem exigir que você copie o hash manualmente.

5. Primeiro confira `http://127.0.0.1:8000/docs`: teste o login, copie o token em Authorize e exercite as rotas. O roteiro está em [VALIDACAO.md](VALIDACAO.md).
6. Em outro CMD, dentro de `frontend/`, execute:

   ```cmd
   python -m http.server 5500
   ```

7. Abra `http://127.0.0.1:5500`. Entre com o e-mail e a senha da conta criada. Mantenha MySQL e os dois servidores ligados durante o uso. O Bootstrap acompanha os arquivos e funciona sem baixar o CSS da internet.

## Funcionalidades

- CRUD de clientes, senioridade, estilos, tatuadores e agendamentos.
- Senioridade por FK e estilos por relacionamento N:N, com checkboxes e listagem agregada.
- Agendamento inicialmente pendente; status aparece na edição.
- Upload de PNG, JPG e WEBP até 5 MB; a miniatura exige sessão autenticada.
- Senhas bcrypt, JWT de duas horas, login, dashboard e logout.
- Cadastro de equipe limitado a administradores; funcionário recebe 403 ao tentar essa ação.
- Configuração de porta e certificado CA para conexão remota.

## Banco, backup e entrega

`banco/estudio_tatuagem.sql` é uma estrutura inicial, não um backup dos cadastros que você criou. Exporte seu banco atualizado pelo phpMyAdmin e guarde essa cópia, conforme as regras da professora. Preserve também `backend/uploads/` se precisar levar os desenhos para outra máquina: o backup SQL guarda o nome do desenho, e não os bytes da imagem.

Para a aula 17, leia [AULA_17_BANCO_REMOTO.md](AULA_17_BANCO_REMOTO.md). O SQL inicial compatível não substitui a conversão e a importação do seu próprio dump. O teste local não comprova a conexão Aiven.

O repositório da professora não foi alterado. Se a entrega exigir GitHub, copie os arquivos para **seu** repositório, confira `git status`, faça commit e push sem incluir `.env`, venv, certificados ou dados pessoais. Histórico de aulas e compreensão teórica não podem ser inferidos apenas pelo funcionamento da aplicação.

As fontes estão em [FONTES.md](FONTES.md); os testes executados e seus limites estão em [VALIDACAO.md](VALIDACAO.md) e `evidencias/`. Use dados fictícios ao testar e esteja preparado para explicar o código durante a apresentação.
