// ─── CRUD de tatuadores, senioridades e relacionamento de estilos ───
protegerPagina()
ativarLogout()
const formTatuador = document.getElementById('form')

// ─── Carrega senioridades e os checkboxes de estilos. ───
async function carregarOpcoes() {
  try {
    const [senioridades, estilos] = await Promise.all([
      api('/senioridade'),
      api('/estilos'),
    ])
    const select = document.getElementById('idsenioridade')
    select.replaceChildren()
    senioridades.forEach((item) => {
      const opcao = document.createElement('option')
      opcao.value = item.idsenioridade
      opcao.textContent = item.nome
      select.append(opcao)
    })
    const lista = document.getElementById('lista-estilos')
    lista.replaceChildren()
    estilos.forEach((item) => {
      const label = document.createElement('label')
      label.className = 'form-check-label'
      const caixa = document.createElement('input')
      caixa.type = 'checkbox'
      caixa.className = 'form-check-input me-1'
      caixa.value = item.idestilo
      label.append(caixa, document.createTextNode(item.descricao))
      lista.append(label)
    })
  } catch (erro) {
    mostrarErro(erro)
  }
}

// ─── Lista tatuadores com senioridade e estilos. ───
async function carregarTatuadores() {
  try {
    const dados = await api('/tatuadores')
    const corpo = document.getElementById('linhas')
    corpo.replaceChildren()
    dados.forEach((item) => {
      const linha = document.createElement('tr')
      celula(linha, item.idtatuador)
      celula(linha, item.nometatuador)
      celula(linha, item.cpf)
      celula(linha, item.email)
      celula(linha, item.telefone)
      celula(linha, item.senioridade)
      celula(linha, item.estilos)
      const acoes = celula(linha, '')
      const editar = document.createElement('button')
      editar.className = 'btn btn-sm btn-outline-primary me-2'
      editar.textContent = 'Editar'
      editar.addEventListener('click', () => editarTatuador(item))
      const excluir = document.createElement('button')
      excluir.className = 'btn btn-sm btn-outline-danger'
      excluir.textContent = 'Excluir'
      excluir.addEventListener('click', async () => {
        if (!confirm('Excluir este tatuador?')) return
        try {
          await api(`/tatuadores/${item.idtatuador}`, { method: 'DELETE' })
          carregarTatuadores()
        } catch (erro) {
          mostrarErro(erro)
        }
      })
      acoes.append(editar, excluir)
      corpo.append(linha)
    })
  } catch (erro) {
    mostrarErro(erro)
  }
}

// ─── Carrega o tatuador e marca seus estilos atuais. ───
async function editarTatuador(item) {
  formTatuador.dataset.id = item.idtatuador
  for (const campo of [
    'nometatuador',
    'cpf',
    'email',
    'telefone',
    'datacontratacao',
    'idsenioridade',
  ])
    document.getElementById(campo).value = item[campo] || ''
  try {
    const estilos = await api(`/tatuadores/${item.idtatuador}/estilos`)
    const marcados = new Set(estilos.map((e) => String(e.idestilo)))
    document.querySelectorAll('#lista-estilos input').forEach((caixa) => {
      caixa.checked = marcados.has(caixa.value)
    })
    document.getElementById('cancelar').hidden = false
  } catch (erro) {
    mostrarErro(erro)
  }
}

// ─── Limpa os campos e retorna ao modo de cadastro. ───
function limparFormulario() {
  formTatuador.reset()
  delete formTatuador.dataset.id
  document.querySelectorAll('#lista-estilos input').forEach((caixa) => {
    caixa.checked = false
  })
  document.getElementById('cancelar').hidden = true
}

// ─── Trata a ação do formulário ou do botão da página ───
formTatuador.addEventListener('submit', async (evento) => {
  evento.preventDefault()
  limparErro()
  const id = formTatuador.dataset.id
  const dados = Object.fromEntries(
    ['nometatuador', 'cpf', 'email', 'telefone', 'datacontratacao'].map(
      (campo) => [campo, document.getElementById(campo).value || null],
    ),
  )
  dados.idsenioridade = Number(document.getElementById('idsenioridade').value)
  const idestilos = [
    ...document.querySelectorAll('#lista-estilos input:checked'),
  ].map((caixa) => Number(caixa.value))
  try {
    const resposta = await api(id ? `/tatuadores/${id}` : '/tatuadores', {
      method: id ? 'PUT' : 'POST',
      body: JSON.stringify(dados),
    })
    const tatuadorId = id || resposta.idtatuador
    formTatuador.dataset.id = tatuadorId // Permite tentar os estilos outra vez sem duplicar o tatuador.
    await api(`/tatuadores/${tatuadorId}/estilos`, {
      method: 'PUT',
      body: JSON.stringify({ idestilos }),
    })
    limparFormulario()
    await carregarTatuadores()
  } catch (erro) {
    mostrarErro(erro)
  }
})
// ─── Trata a ação do formulário ou do botão da página ───
document.getElementById('cancelar').addEventListener('click', limparFormulario)
carregarOpcoes().then(carregarTatuadores)
