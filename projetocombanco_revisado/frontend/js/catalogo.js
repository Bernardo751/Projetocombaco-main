// ─── Compartilha a lógica de CRUD das telas de estilos e senioridade ───
function iniciarCatalogo({ recurso, campo, chave, singular }) {
  protegerPagina()
  ativarLogout()
  const formulario = document.getElementById('form')
  const botaoSalvar = formulario.querySelector('[type="submit"]')

  // ─── Devolve o formulário ao modo de cadastro ───
  function limparFormulario() {
    formulario.reset()
    delete formulario.dataset.id
    document.getElementById('cancelar').hidden = true
    botaoSalvar.textContent = 'Cadastrar'
  }

  // ─── Leva o registro selecionado para edição ───
  function editarItem(item) {
    document.getElementById('valor').value = item[campo]
    formulario.dataset.id = item[chave]
    document.getElementById('cancelar').hidden = false
    botaoSalvar.textContent = 'Salvar alteração'
  }

  // ─── Exclui o registro após a confirmação do usuário ───
  async function excluirItem(id) {
    if (!confirm(`Excluir este registro de ${singular}?`)) return
    limparErro()
    try {
      await api(`/${recurso}/${id}`, { method: 'DELETE' })
      if (Number(formulario.dataset.id) === id) limparFormulario()
      await carregarItens()
    } catch (erro) {
      mostrarErro(erro)
    }
  }

  // ─── Lista os dados e cria os botões de cada linha ───
  async function carregarItens() {
    try {
      const itens = await api(`/${recurso}`)
      const corpo = document.getElementById('linhas')
      corpo.replaceChildren()
      itens.forEach((item) => {
        const linha = document.createElement('tr')
        celula(linha, item[chave])
        celula(linha, item[campo])
        const acoes = celula(linha, '')
        const editar = document.createElement('button')
        editar.className = 'btn btn-sm btn-outline-primary me-2'
        editar.textContent = 'Editar'
        editar.addEventListener('click', () => editarItem(item))
        const excluir = document.createElement('button')
        excluir.className = 'btn btn-sm btn-outline-danger'
        excluir.textContent = 'Excluir'
        excluir.addEventListener('click', () => excluirItem(item[chave]))
        acoes.append(editar, excluir)
        corpo.append(linha)
      })
    } catch (erro) {
      mostrarErro(erro)
    }
  }

  // ─── Salva sem perder a referência do formulário depois do await ───
  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault()
    limparErro()
    const id = formulario.dataset.id
    botaoSalvar.disabled = true
    try {
      await api(id ? `/${recurso}/${id}` : `/${recurso}`, {
        method: id ? 'PUT' : 'POST',
        body: JSON.stringify({
          [campo]: document.getElementById('valor').value,
        }),
      })
      limparFormulario()
      await carregarItens()
    } catch (erro) {
      mostrarErro(erro)
    } finally {
      botaoSalvar.disabled = false
    }
  })

  // ─── Inicializa a tela e o botão para cancelar a edição ───
  document
    .getElementById('cancelar')
    .addEventListener('click', limparFormulario)
  carregarItens()
}
