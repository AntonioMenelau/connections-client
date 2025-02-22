document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    
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

    socket.emit('carregarUsuarios');
  });
  