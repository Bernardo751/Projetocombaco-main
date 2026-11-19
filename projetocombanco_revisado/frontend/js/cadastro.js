// ─── Cadastro de usuário de equipe, disponível somente a administradores ───
exigirAdminNaTela()
ativarLogout()
// ─── Trata a ação do formulário ou do botão da página ───
document
  .getElementById('form-cadastro')
  .addEventListener('submit', async (evento) => {
    evento.preventDefault()
    limparErro()
    try {
      await api('/usuarios', {
        method: 'POST',
        body: JSON.stringify({
          nome: document.getElementById('nome').value,
          email: document.getElementById('email').value,
          senha: document.getElementById('senha').value,
          tipo: document.getElementById('tipo').value,
        }),
      })
      evento.target.reset()
      document.getElementById('sucesso').textContent = 'Usuário cadastrado.'
    } catch (erro) {
      mostrarErro(erro)
    }
  })
