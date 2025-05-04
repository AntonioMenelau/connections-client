let selectedElement = null;
let isPanning = false;
let startX, startY;
let translateX = 0, translateY = 0;
const canvasElements = new Map();
const canvasContainer = document.getElementById('canvasContainer');
let locEquipamentos = {};

document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const listaUsuarios = document.getElementById('listaUsuarios');
    const searchInput = document.getElementById('searchInput');

    // Sistema de busca
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        Array.from(listaUsuarios.children).forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(searchTerm) ? 'block' : 'none';
        });
    });

    // Atualização de status em tempo real
    socket.on('atualizar_lista', (data) => {
        updateUserList(data.usuarios);
        updateCanvasElements(data.usuarios);
    });

    const updateUserList = (usuarios) => {
        listaUsuarios.innerHTML = '';
        usuarios.forEach(usuario => createUserListItem(usuario));
    };

    const createUserListItem = (usuario) => {
        const li = document.createElement('li');
        li.className = 'bg-white p-4 rounded shadow mb-2 draggable cursor-move';
        li.draggable = true;
        li.dataset.usuario = JSON.stringify(usuario);

        const container = document.createElement('div');
        container.className = 'flex items-center justify-between';

        const info = document.createElement('div');
        info.innerHTML = `
            ${usuario[0]} - 
            <span class="${usuario[1] === 'online' ? 'text-green-500' : 'text-red-500'}">
                ${usuario[1]}
            </span>
        `;


        container.appendChild(info);
        li.appendChild(container);

        const detalhes = document.createElement('div');
        detalhes.className = 'mt-2 text-sm text-gray-600 hidden';
        detalhes.innerHTML = usuario[2].replace(/\n/g, '<br>');
        li.appendChild(detalhes);
        li.addEventListener('dragstart', handleDragStart);
        li.addEventListener('dragend', handleDragEnd);

        listaUsuarios.appendChild(li);
    };

    const updateCanvasElements = (usuarios) => {
        usuarios.forEach(usuario => {
            const element = canvasElements.get(usuario[0]);
            if (element) {
                element.className = `absolute cursor-pointer hover:shadow-lg p-2 rounded-full 
                                    flex items-center justify-center text-white font-bold text-[12px]
                                    ${usuario[1] === 'online' ? 'bg-green-500' : 'bg-red-500'}`;
                element.dataset.info = usuario[2]; // <-- Atualiza as informações!
                element.dataset.usuario = JSON.stringify(usuario); // <-- Atualiza o objeto completo!
            }
        });
    };

    const createCanvasElement = (usuario, x, y) => {
        // Remove elemento existente se já existir
        if (canvasElements.has(usuario[0])) {
            canvasElements.get(usuario[0]).remove();
        }
    
        const element = document.createElement('div');
        element.className = `absolute cursor-pointer hover:shadow-lg p-2 rounded-full 
                               flex items-center justify-center text-white font-bold text-[12px]
                               ${usuario[1] === 'online' ? 'bg-green-500' : 'bg-red-500'}`;
        element.style.left = `${x}px`;
        element.style.top = `${y}px`;
        // Exibe apenas as 5 primeiras letras
        element.textContent = usuario[0].substring(0, 5);
        element.dataset.info = usuario[2];
        element.dataset.usuario = JSON.stringify(usuario);
    
        // Evento para exibir o nome completo quando o mouse entrar
        element.addEventListener('mouseenter', () => {
            element.textContent = usuario[0];
            element.style.zIndex = 999;
        });
        
        // Evento para retornar ao nome reduzido quando o mouse sair
        element.addEventListener('mouseleave', () => {
            element.textContent = usuario[0].substring(0, 5);
            element.style.zIndex = '';
        });
    
        element.addEventListener('contextmenu', handleContextMenu);
    
        canvasArea.appendChild(element);
        canvasElements.set(usuario[0], element);
        return element;
    };

    // Event handlers
    const handleDragStart = (e) => {
        e.dataTransfer.setData('usuario', e.target.dataset.usuario);
    };

    const handleDragEnd = (e) => {
        e.target.classList.remove('opacity-50');
    };

    const handleContextMenu = (e) => {
        e.preventDefault();
        selectedElement = e.target;
        const contextMenu = document.getElementById('contextMenu');
        contextMenu.style.left = `${e.clientX}px`;
        contextMenu.style.top = `${e.clientY}px`;
        contextMenu.classList.remove('hidden');
    };

    const toggleDetails = (detalhes, btn) => {
        detalhes.classList.toggle('hidden');
        btn.textContent = detalhes.classList.contains('hidden') 
            ? 'Mostrar detalhes' 
            : 'Ocultar detalhes';
    };

    // Canvas drop handler
    canvasArea.addEventListener('dragover', (e) => e.preventDefault());
    
    canvasArea.addEventListener('drop', (e) => {
        e.preventDefault();
        const usuarioData = e.dataTransfer.getData('usuario');
        if (!usuarioData) return;

        const usuario = JSON.parse(usuarioData);
        const rect = canvasArea.getBoundingClientRect();
        const x = e.clientX - rect.left - translateX;
        const y = e.clientY - rect.top - translateY;

        createCanvasElement(usuario, x, y);
        locEquipamentos[usuario[0]] = {usuario, x, y};
    });


    // Context menu handlers
    document.getElementById('deleteOption').addEventListener('click', () => {
        if (selectedElement) {
            const usuario = JSON.parse(selectedElement.dataset.usuario);
            canvasElements.get(usuario[0]).remove();
            canvasElements.delete(usuario[0]);
            document.getElementById('contextMenu').classList.add('hidden');
        }
    });

    document.getElementById('infoOption').addEventListener('click', () => {
        if (selectedElement) {
            document.getElementById('infoContent').textContent = selectedElement.dataset.info;
            document.getElementById('sidebar').classList.remove('hidden');
            document.getElementById('contextMenu').classList.add('hidden');
        }
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('#contextMenu')) {
            document.getElementById('contextMenu').classList.add('hidden');
        }
    });

    socket.emit('carregarUsuarios');
});