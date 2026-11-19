// ─── Exige login, ativa a saída e mostra a ação administrativa conforme o perfil ───
protegerPagina()
ativarLogout()
if (localStorage.getItem('tipo') !== 'admin')
  document.getElementById('admin-card').hidden = true
