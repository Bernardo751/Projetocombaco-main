// ─── CRUD de sessões, listas relacionadas e upload privado de desenho ───
protegerPagina()
ativarLogout()
const formAgendamento = document.getElementById('form')

// ─── Busca clientes e tatuadores para preencher as opções. ───
async function carregarSelects() {
  try {
    const [clientes, tatuadores] = await Promise.all([
      api('/clientes'),
      api('/tatuadores'),
    ])
    for (const [id, lista, chave, nome] of [
      ['idcliente', clientes, 'idcliente', 'nome'],
      ['idtatuador', tatuadores, 'idtatuador', 'nometatuador'],
    ]) {
      const select = document.getElementById(id)
      select.replaceChildren()
      lista.forEach((item) => {
        const op = document.createElement('option')
        op.value = item[chave]
        op.textContent = item[nome]
        select.append(op)
      })
    }
  } catch (erro) {
    mostrarErro(erro)
  }
}

// ─── Obtém o desenho aprovado com o token da sessão. ───
async function colocarMiniatura(celulaDesenho, nome) {
  if (!nome) {
    celulaDesenho.textContent = '—'
    return
  }
  try {
    const resposta = await fetchAutenticado(
      `${API_URL}/uploads/${encodeURIComponent(nome)}`,
      { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } },
    )
    if (!resposta.ok) throw new Error('Imagem indisponível')
    const img = document.createElement('img')
    img.src = URL.createObjectURL(await resposta.blob())
    img.alt = 'Desenho aprovado'
    img.width = 64
    img.height = 64
    img.className = 'object-fit-cover rounded'
    img.addEventListener('load', () => URL.revokeObjectURL(img.src), {
      once: true,
    })
    celulaDesenho.append(img)
  } catch {
    celulaDesenho.textContent = 'Indisponível'
  }
}

// ─── Carrega a tabela de agendamentos e suas miniaturas. ───
async function carregarAgendamentos() {
  try {
    const itens = await api('/agendamentos')
    const corpo = document.getElementById('linhas')
    corpo.replaceChildren()
    for (const item of itens) {
      const linha = document.createElement('tr')
      ;[
        item.idagendamento,
        item.dataagendamento,
        item.horaagendamento,
        item.cliente,
        item.tatuador,
        item.descricaotatuagem,
        item.valortatuagem == null
          ? '—'
          : `R$ ${Number(item.valortatuagem).toFixed(2)}`,
        item.status,
      ].forEach((v) => celula(linha, v))
      const imagem = celula(linha, '')
      await colocarMiniatura(imagem, item.desenhoaprovado)
      const acoes = celula(linha, '')
      const editar = document.createElement('button')
      editar.className = 'btn btn-sm btn-outline-primary me-2'
      editar.textContent = 'Editar'
      editar.addEventListener('click', () => editarAgendamento(item))
      const excluir = document.createElement('button')
      excluir.className = 'btn btn-sm btn-outline-danger'
      excluir.textContent = 'Excluir'
      excluir.addEventListener('click', async () => {
        if (!confirm('Excluir este agendamento?')) return
        try {
          await api(`/agendamentos/${item.idagendamento}`, { method: 'DELETE' })
          carregarAgendamentos()
        } catch (erro) {
          mostrarErro(erro)
        }
      })
      acoes.append(editar, excluir)
      corpo.append(linha)
    }
  } catch (erro) {
    mostrarErro(erro)
  }
}

// ─── Preenche o formulário e mostra o status somente na edição. ───
function editarAgendamento(item) {
  formAgendamento.dataset.id = item.idagendamento
  for (const campo of [
    'idcliente',
    'idtatuador',
    'dataagendamento',
    'horaagendamento',
    'descricaotatuagem',
    'valortatuagem',
    'status',
  ])
    document.getElementById(campo).value = item[campo] ?? ''
  document.getElementById('bloco-status').hidden = false
  document.getElementById('cancelar').hidden = false
}

// ─── Limpa os campos e retorna ao modo de cadastro. ───
function limparFormulario() {
  formAgendamento.reset()
  delete formAgendamento.dataset.id
  document.getElementById('bloco-status').hidden = true
  document.getElementById('cancelar').hidden = true
}

// ─── Trata a ação do formulário ou do botão da página ───
formAgendamento.addEventListener('submit', async (evento) => {
  evento.preventDefault()
  limparErro()
  const id = formAgendamento.dataset.id
  const dados = {
    idcliente: Number(document.getElementById('idcliente').value),
    idtatuador: Number(document.getElementById('idtatuador').value),
    dataagendamento: document.getElementById('dataagendamento').value,
    horaagendamento: document.getElementById('horaagendamento').value,
    descricaotatuagem:
      document.getElementById('descricaotatuagem').value || null,
    valortatuagem: document.getElementById('valortatuagem').value
      ? Number(document.getElementById('valortatuagem').value)
      : null,
  }
  if (id) dados.status = document.getElementById('status').value
  try {
    const resposta = await api(id ? `/agendamentos/${id}` : '/agendamentos', {
      method: id ? 'PUT' : 'POST',
      body: JSON.stringify(dados),
    })
    const novoId = id || resposta.idagendamento
    formAgendamento.dataset.id = novoId
    document.getElementById('bloco-status').hidden = false
    const arquivo = document.getElementById('desenho').files[0]
    if (arquivo) {
      const pacote = new FormData()
      pacote.append('arquivo', arquivo)
      await api(`/agendamentos/${novoId}/desenho`, {
        method: 'POST',
        body: pacote,
      })
    }
    limparFormulario()
    await carregarAgendamentos()
  } catch (erro) {
    mostrarErro(erro)
  }
})
// ─── Trata a ação do formulário ou do botão da página ───
document.getElementById('cancelar').addEventListener('click', limparFormulario)
carregarSelects().then(carregarAgendamentos)
