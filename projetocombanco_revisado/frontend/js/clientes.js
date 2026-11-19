// ─── CRUD de clientes ───
protegerPagina()
ativarLogout()
const formCliente = document.getElementById('form')
let clientes = []

// ─── Busca os clientes e monta as linhas da tabela. ───
async function carregarClientes() {
  limparErro()
  try {
    clientes = await api('/clientes')
    const corpo = document.getElementById('linhas')
    corpo.replaceChildren()
    clientes.forEach((cliente) => {
      const linha = document.createElement('tr')
      ;[
        cliente.idcliente,
        cliente.nome,
        cliente.cpf,
        cliente.telefone,
        cliente.cidade,
        cliente.uf,
      ].forEach((valor) => celula(linha, valor))
      const acoes = celula(linha, '')
      const editar = document.createElement('button')
      editar.className = 'btn btn-sm btn-outline-primary me-2'
      editar.textContent = 'Editar'
      editar.addEventListener('click', () => editarCliente(cliente))
      const excluir = document.createElement('button')
      excluir.className = 'btn btn-sm btn-outline-danger'
      excluir.textContent = 'Excluir'
      excluir.addEventListener('click', () => excluirCliente(cliente.idcliente))
      acoes.append(editar, excluir)
      corpo.append(linha)
    })
  } catch (erro) {
    mostrarErro(erro)
  }
}

// ─── Preenche os dados do cliente selecionado para edição. ───
function editarCliente(cliente) {
  formCliente.dataset.id = cliente.idcliente
  formCliente.dataset.datacadastro = cliente.datacadastro || ''
  for (const campo of ['nome', 'cpf', 'telefone', 'cidade', 'uf'])
    document.getElementById(campo).value = cliente[campo] || ''
  document.getElementById('cancelar').hidden = false
  formCliente.querySelector('[type="submit"]').textContent = 'Salvar alterações'
}

// ─── Cancela a edição e restaura o formulário de cadastro. ───
function limparEdicao() {
  formCliente.reset()
  delete formCliente.dataset.id
  delete formCliente.dataset.datacadastro
  document.getElementById('cancelar').hidden = true
  formCliente.querySelector('[type="submit"]').textContent = 'Salvar cliente'
}

// ─── Exclui o cliente após confirmação e atualiza a tabela. ───
async function excluirCliente(id) {
  if (!confirm('Excluir este cliente?')) return
  try {
    await api(`/clientes/${id}`, { method: 'DELETE' })
    await carregarClientes()
  } catch (erro) {
    mostrarErro(erro)
  }
}

// ─── Trata a ação do formulário ou do botão da página ───
formCliente.addEventListener('submit', async (evento) => {
  evento.preventDefault()
  limparErro()
  const dados = Object.fromEntries(
    ['nome', 'cpf', 'telefone', 'cidade', 'uf'].map((campo) => [
      campo,
      document.getElementById(campo).value || null,
    ]),
  )
  dados.datacadastro = formCliente.dataset.id
    ? formCliente.dataset.datacadastro || null
    : dataHoje()
  try {
    const id = formCliente.dataset.id
    await api(id ? `/clientes/${id}` : '/clientes', {
      method: id ? 'PUT' : 'POST',
      body: JSON.stringify(dados),
    })
    limparEdicao()
    await carregarClientes()
  } catch (erro) {
    mostrarErro(erro)
  }
})
// ─── Trata a ação do formulário ou do botão da página ───
document.getElementById('cancelar').addEventListener('click', limparEdicao)
carregarClientes()
