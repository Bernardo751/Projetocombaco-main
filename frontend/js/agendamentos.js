javascript
// Endereço da API backend
const API = 'http://127.0.0.1:8000'

// Elementos do formulário
const formAgendamento = document.getElementById('form-agendamento')
const botaoSubmit = document.getElementById('btn-submit-agendamento')
const blocoStatus = document.getElementById('bloco-status')

// Limpa o formulário e volta ao modo de cadastro
function limparFormulario() {
  formAgendamento.reset()

  delete formAgendamento.dataset.idAgendamento

  botaoSubmit.textContent = 'Cadastrar'
  botaoSubmit.classList.remove('btn-success')
  botaoSubmit.classList.add('btn-primary')

  blocoStatus.style.display = 'none'
}

// Busca os clientes e preenche o select
async function carregarClientes() {
  try {
    const resposta = await fetch(`${API}/clientes`)

    if (!resposta.ok) {
      throw new Error('Erro ao carregar clientes')
    }

    const clientes = await resposta.json()
    const select = document.getElementById('idcliente')

    select.innerHTML = '<option value="">Cliente...</option>'

    clientes.forEach(c => {
      select.innerHTML += `
        <option value="${c.idcliente}">${c.nome}</option>
      `
    })
  } catch (erro) {
    console.error(erro)
    alert('Não foi possível carregar os clientes.')
  }
}

// Busca os tatuadores e preenche o select
async function carregarTatuadores() {
  try {
    const resposta = await fetch(`${API}/tatuadores`)

    if (!resposta.ok) {
      throw new Error('Erro ao carregar tatuadores')
    }

    const tatuadores = await resposta.json()
    const select = document.getElementById('idtatuador')

    select.innerHTML = '<option value="">Tatuador...</option>'

    tatuadores.forEach(t => {
      select.innerHTML += `
        <option value="${t.idtatuador}">${t.nometatuador}</option>
      `
    })
  } catch (erro) {
    console.error(erro)
    alert('Não foi possível carregar os tatuadores.')
  }
}

// Carrega os dados iniciais
carregarClientes()
carregarTatuadores()

// Lista os agendamentos na tabela
async function listarAgendamentos() {
  try {
    const resposta = await fetch(`${API}/agendamentos`)

    if (!resposta.ok) {
      throw new Error('Erro ao buscar agendamentos')
    }

    const agendamentos = await resposta.json()
    const corpo = document.getElementById('corpo-tabela')

    corpo.innerHTML = ''

    agendamentos.forEach(a => {
      // Monta a miniatura se houver desenho salvo
      const imagemHtml = a.desenhoaprovado
        ? `<a href="${API}/uploads/${encodeURIComponent(a.desenhoaprovado)}" target="_blank" rel="noopener noreferrer">
             <img
               src="${API}/uploads/${encodeURIComponent(a.desenhoaprovado)}"
               alt="Desenho do agendamento ${a.idagendamento}"
               style="max-width: 60px; max-height: 60px; object-fit: contain;"
             >
           </a>`
        : '-'

      const linha = document.createElement('tr')

      // Monta as células sem inserir os dados textuais diretamente como HTML
      const valores = [
        a.idagendamento,
        a.cliente,
        a.tatuador,
        a.dataagendamento,
        a.horaagendamento,
        a.valortatuagem ?? '-',
        a.status ?? '-'
      ]

      valores.forEach(valor => {
        const celula = document.createElement('td')
        celula.textContent = valor ?? '-'
        linha.appendChild(celula)
      })

      const celulaImagem = document.createElement('td')
      celulaImagem.innerHTML = imagemHtml
      linha.appendChild(celulaImagem)

      const celulaAcoes = document.createElement('td')

      const botaoEditar = document.createElement('button')
      botaoEditar.type = 'button'
      botaoEditar.className = 'btn btn-sm btn-warning me-2'
      botaoEditar.textContent = 'Editar'
      botaoEditar.addEventListener('click', () => {
        preencherFormularioEdicao(a)
      })

      const botaoExcluir = document.createElement('button')
      botaoExcluir.type = 'button'
      botaoExcluir.className = 'btn btn-sm btn-danger'
      botaoExcluir.textContent = 'Excluir'
      botaoExcluir.addEventListener('click', () => {
        deletarAgendamento(a.idagendamento)
      })

      celulaAcoes.appendChild(botaoEditar)
      celulaAcoes.appendChild(botaoExcluir)
      linha.appendChild(celulaAcoes)

      corpo.appendChild(linha)
    })
  } catch (erro) {
    console.error(erro)
    alert('Não foi possível carregar os agendamentos.')
  }
}

listarAgendamentos()

// Cadastra ou atualiza um agendamento e, se selecionada, envia a imagem
formAgendamento.addEventListener('submit', async (e) => {
  e.preventDefault()

  const agendamento = {
    idcliente: Number(document.getElementById('idcliente').value),
    idtatuador: Number(document.getElementById('idtatuador').value),
    dataagendamento: document.getElementById('dataagendamento').value,
    horaagendamento: document.getElementById('horaagendamento').value,
    descricaotatuagem:
      document.getElementById('descricaotatuagem').value || null,
    valortatuagem: document.getElementById('valortatuagem').value
      ? Number(document.getElementById('valortatuagem').value)
      : null,
    status: document.getElementById('status').value || null
  }

  const arquivo = document.getElementById('desenho').files[0]
  const idAgendamento = formAgendamento.dataset.idAgendamento

  // Validação básica da imagem
  if (arquivo) {
    const tiposPermitidos = [
      'image/jpeg',
      'image/png',
      'image/webp',
      'image/gif'
    ]

    if (!tiposPermitidos.includes(arquivo.type)) {
      alert('Selecione uma imagem JPG, PNG, WEBP ou GIF.')
      return
    }

    if (arquivo.size > 5 * 1024 * 1024) {
      alert('A imagem deve ter no máximo 5 MB.')
      return
    }
  }

  botaoSubmit.disabled = true

  try {
    let idParaUpload

    if (idAgendamento) {
      // Atualiza o agendamento existente
      const resposta = await fetch(
        `${API}/agendamentos/${idAgendamento}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(agendamento)
        }
      )

      if (!resposta.ok) {
        throw new Error('Erro ao atualizar o agendamento')
      }

      idParaUpload = idAgendamento
    } else {
      // Cadastra um novo agendamento
      const resposta = await fetch(`${API}/agendamentos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(agendamento)
      })

      if (!resposta.ok) {
        throw new Error('Erro ao cadastrar o agendamento')
      }

      const dados = await resposta.json()
      idParaUpload = dados.idagendamento

      if (!idParaUpload) {
        throw new Error('A API não retornou o ID do agendamento')
      }
    }

    // Envia a imagem em uma segunda requisição
    if (arquivo) {
      const formData = new FormData()
      formData.append('arquivo', arquivo)

      const respostaUpload = await fetch(
        `${API}/agendamentos/${idParaUpload}/desenho`,
        {
          method: 'POST',
          body: formData
        }
      )

      if (!respostaUpload.ok) {
        const erroUpload = await respostaUpload.json().catch(() => ({}))

        throw new Error(
          erroUpload.detail || 'O agendamento foi salvo, mas a imagem não foi enviada'
        )
      }
    }

    alert(
      arquivo
        ? 'Agendamento salvo e desenho enviado com sucesso!'
        : 'Agendamento salvo com sucesso!'
    )

    limparFormulario()
    await listarAgendamentos()

  } catch (erro) {
    console.error(erro)
    alert(erro.message || 'Ocorreu um erro ao salvar o agendamento.')
  } finally {
    botaoSubmit.disabled = false
  }
})

// Preenche o formulário para editar um agendamento
function preencherFormularioEdicao(agendamento) {
  document.getElementById('idcliente').value = agendamento.idcliente
  document.getElementById('idtatuador').value = agendamento.idtatuador

  document.getElementById('dataagendamento').value =
    String(agendamento.dataagendamento).slice(0, 10)

  document.getElementById('horaagendamento').value =
    String(agendamento.horaagendamento).slice(0, 5)

  document.getElementById('descricaotatuagem').value =
    agendamento.descricaotatuagem || ''

  document.getElementById('valortatuagem').value =
    agendamento.valortatuagem ?? ''

  document.getElementById('status').value =
    agendamento.status || 'pendente'

  // O navegador não permite preencher automaticamente um input de arquivo.
  // Se nenhum arquivo novo for escolhido, o desenho existente será mantido.
  document.getElementById('desenho').value = ''

  blocoStatus.style.display = 'block'

  formAgendamento.dataset.idAgendamento = agendamento.idagendamento

  botaoSubmit.textContent = 'Salvar alteração'
  botaoSubmit.classList.remove('btn-primary')
  botaoSubmit.classList.add('btn-success')

  formAgendamento.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  })
}

// Exclui um agendamento
async function deletarAgendamento(id) {
  if (!confirm('Tem certeza que deseja excluir este agendamento?')) {
    return
  }

  try {
    const resposta = await fetch(`${API}/agendamentos/${id}`, {
      method: 'DELETE'
    })

    if (!resposta.ok) {
      throw new Error('Erro ao excluir o agendamento')
    }

    alert('Agendamento excluído com sucesso!')

    if (formAgendamento.dataset.idAgendamento === String(id)) {
      limparFormulario()
    }

    await listarAgendamentos()
  } catch (erro) {
    console.error(erro)
    alert(erro.message || 'Não foi possível excluir o agendamento.')
  }
}