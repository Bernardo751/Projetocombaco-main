// ─── Endereço do backend usado pelas telas ───
const API_URL = 'http://127.0.0.1:8000'

// ─── Converte erros de validação da API em uma mensagem legível ───
function descreverErro(corpo, status) {
  if (Array.isArray(corpo.detail)) {
    return corpo.detail
      .map((item) => `${item.loc.slice(1).join('.')}: ${item.msg}`)
      .join('; ')
  }
  return corpo.detail || corpo.erro || `A requisição falhou (HTTP ${status}).`
}

// ─── Envia JSON ou FormData e trata a resposta da API ───
async function api(caminho, opcoes = {}) {
  const cabecalhos = new Headers(opcoes.headers || {})
  // FormData precisa do Content-Type e do boundary gerados pelo próprio navegador.
  if (opcoes.body && !(opcoes.body instanceof FormData))
    cabecalhos.set('Content-Type', 'application/json')
  let resposta
  try {
    const enviar =
      typeof fetchAutenticado === 'function' ? fetchAutenticado : fetch
    resposta = await enviar(`${API_URL}${caminho}`, {
      ...opcoes,
      headers: cabecalhos,
    })
  } catch (erro) {
    if (erro instanceof TypeError)
      throw new Error(
        'Não foi possível acessar a API. Confira se o backend está ligado na porta 8000.',
      )
    throw erro
  }
  if (resposta.status === 204) return null
  const corpo = await resposta.json().catch(() => ({}))
  if (!resposta.ok) throw new Error(descreverErro(corpo, resposta.status))
  return corpo
}

// ─── Mostra na página o motivo da falha ───
function mostrarErro(erro) {
  const aviso = document.getElementById('aviso')
  if (aviso)
    aviso.textContent = erro.message || 'Não foi possível concluir a operação.'
}

// ─── Remove o aviso da operação anterior ───
function limparErro() {
  const aviso = document.getElementById('aviso')
  if (aviso) aviso.textContent = ''
}

// ─── Acrescenta texto à tabela sem interpretar conteúdo como HTML ───
function celula(linha, valor) {
  const td = document.createElement('td')
  td.textContent = valor ?? '—'
  linha.append(td)
  return td
}

// ─── Calcula a data local sem deslocamento pelo fuso horário UTC ───
function dataHoje() {
  const hoje = new Date()
  return `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}-${String(hoje.getDate()).padStart(2, '0')}`
}
