// ─── Valida credenciais e guarda o token de sessão ───
// ─── Trata a ação do formulário ou do botão da página ───
document
  .getElementById('form-login')
  .addEventListener('submit', async (evento) => {
    evento.preventDefault()
    const aviso = document.getElementById('aviso')
    aviso.textContent = ''
    try {
      const resposta = await api('/login', {
        method: 'POST',
        body: JSON.stringify({
          email: document.getElementById('email').value,
          senha: document.getElementById('senha').value,
        }),
      })
      localStorage.setItem('token', resposta.access_token)
      localStorage.setItem('tipo', resposta.tipo)
      location.href = './dashboard.html'
    } catch (erro) {
      aviso.textContent = erro.message
    }
  })
