// ─── Redireciona para o login quando não existe uma sessão no navegador ───
function protegerPagina() {
  if (!localStorage.getItem('token')) location.href = './login.html'
}

// ─── Anexa o token às requisições e encerra a sessão quando a API devolve 401 ───
async function fetchAutenticado(url, opcoes = {}) {
  const headers = new Headers(opcoes.headers || {})
  const token = localStorage.getItem('token')
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const resposta = await fetch(url, { ...opcoes, headers })
  if (resposta.status === 401) {
    localStorage.removeItem('token')
    localStorage.removeItem('tipo')
    location.href = './login.html'
    throw new Error('Sua sessão terminou. Entre novamente.')
  }
  return resposta
}

// ─── Orienta a navegação administrativa; a permissão real é conferida pela API ───
function exigirAdminNaTela() {
  protegerPagina()
  if (localStorage.getItem('token') && localStorage.getItem('tipo') !== 'admin')
    location.href = './dashboard.html'
}

// ─── Apaga a sessão local e retorna ao login ───
function sair() {
  localStorage.removeItem('token')
  localStorage.removeItem('tipo')
  location.href = './login.html'
}

// ─── Liga os botões Sair ao encerramento da sessão ───
function ativarLogout() {
  document
    .querySelectorAll('[data-logout]')
    .forEach((botao) => botao.addEventListener('click', sair))
}
