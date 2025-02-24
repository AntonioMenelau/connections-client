document.addEventListener('DOMContentLoaded', () => {
  const socket = io();
  const listaUsuarios = document.getElementById('listaUsuarios');

  // Recebe atualizações da lista de usuários
  socket.on('atualizar_lista', (data) => {
      const usuarios = data.usuarios;
      listaUsuarios.innerHTML = ''; // Limpa a lista atual
      usuarios.forEach(usuario => {
          console.log(usuario);
          
          // Cria o elemento li para o usuário
          const li = document.createElement('li');
          li.className = 'bg-white p-4 rounded shadow mb-2';

          // Cria um container para os dados principais
          const containerPrincipal = document.createElement('div');
          containerPrincipal.className = 'flex items-center justify-between';

          // Cria o texto do usuário e status
          const infoUsuario = document.createElement('div');
          infoUsuario.textContent = `${usuario[0]} - `;
          
          const spanStatus = document.createElement('span');
          spanStatus.textContent = usuario[1];
          spanStatus.className = usuario[1] === 'online' ? 'text-green-500' : 'text-red-500';
          infoUsuario.appendChild(spanStatus);
          
          containerPrincipal.appendChild(infoUsuario);

          // Cria o botão para expandir/recolher
          const btnToggle = document.createElement('button');
          btnToggle.textContent = 'Mostrar detalhes';
          btnToggle.className = 'text-blue-500 hover:underline focus:outline-none';
          containerPrincipal.appendChild(btnToggle);

          li.appendChild(containerPrincipal);

          // Cria o div com os detalhes, já substituindo as quebras de linha
          const detalhesDiv = document.createElement('div');
          detalhesDiv.className = 'mt-2 text-sm text-gray-600 hidden';
          detalhesDiv.innerHTML = usuario[2].replace(/\n/g, '<br>');
          li.appendChild(detalhesDiv);

          // Adiciona o evento para alternar a visibilidade dos detalhes
          btnToggle.addEventListener('click', () => {
              if(detalhesDiv.classList.contains('hidden')) {
                  detalhesDiv.classList.remove('hidden');
                  btnToggle.textContent = 'Ocultar detalhes';
              } else {
                  detalhesDiv.classList.add('hidden');
                  btnToggle.textContent = 'Mostrar detalhes';
              }
          });

          listaUsuarios.appendChild(li);
      });
  });

  socket.emit('carregarUsuarios');
});
