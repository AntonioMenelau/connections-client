document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
  
    let username = '';
  
    const btnConectar = document.getElementById('btnConectar');
    const inputUsername = document.getElementById('username');
    const listaUsuarios = document.getElementById('listaUsuarios');
  
    btnConectar.addEventListener('click', () => {
      username = inputUsername.value.trim();
      if (username) {
        // Registra o usuário no servidor
        socket.emit('registrar_usuario', { username: username });
      }
    });
  
    // Recebe atualizações da lista de usuários
    socket.on('atualizar_lista', (data) => {
      const usuarios = data.usuarios;
      listaUsuarios.innerHTML = ''; // Limpa a lista atual
      usuarios.forEach(usuario => {
        const li = document.createElement('li');
        li.textContent = `${usuario[0]} - `;
        const span = document.createElement('span');
        span.textContent = usuario[1];
        span.className = usuario[1] === 'online' ? 'online' : 'offline';
        li.appendChild(span);
        listaUsuarios.appendChild(li);
      });
    });
  
    // Quando o usuário fechar a página, avisa o servidor
    window.addEventListener('beforeunload', () => {
      if (username) {
        socket.emit('usuario_desconectando', { username: username });
      }
    });
  });
  