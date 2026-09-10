const API = 'http://127.0.0.1:8000'  // endereço da nossa API
const formCliente = document.getElementById('form-cliente')
const botaoSubmit = document.getElementById('btn-submit-cliente')

function limparFormulario() {
  formCliente.reset()
  delete formCliente.dataset.idCliente
  botaoSubmit.textContent = 'Cadastrar'
  botaoSubmit.classList.remove('btn-success')
  botaoSubmit.classList.add('btn-primary')
}

async function listarClientes() {
  const resposta = await fetch(`${API}/clientes`)
  const clientes = await resposta.json()

  const corpo = document.getElementById('corpo-tabela')
  corpo.innerHTML = ''

  clientes.forEach(c => {
    corpo.innerHTML += `
      <tr>
        <td>${c.idcliente}</td>
        <td>${c.nome}</td>
        <td>${c.cpf}</td>
        <td>${c.telefone ?? '-'}</td>
        <td>${c.cidade ?? '-'}</td>
        <td>${c.uf ?? '-'}</td>
        <td>
          <button class="btn btn-sm btn-warning me-2" onclick='preencherFormularioEdicao(${JSON.stringify(c)})'>Editar</button>
          <button class="btn btn-sm btn-danger" onclick="deletarCliente(${c.idcliente})">Excluir</button>
        </td>
      </tr>`
  })
}

listarClientes()