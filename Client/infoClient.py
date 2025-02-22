import platform
import socket
import psutil
import os
import cpuinfo
import socketio
import atexit
import time
import threading

# Função para coletar informações do sistema
def coletar_informacoes():
    info = {}
    # Informações do Sistema Operacional
    info['Sistema Operacional'] = platform.system()
    info['Versão do SO'] = platform.version()
    info['Nome do SO'] = platform.platform()
    info['Arquitetura'] = platform.machine()
    
    # Informações do Usuário e Computador
    info['Nome do Usuário'] = os.getlogin()
    info['Nome do Computador'] = socket.gethostname()
    try:
        info['Endereço IP'] = socket.gethostbyname(socket.gethostname())
    except Exception:
        info['Endereço IP'] = 'N/A'
    
    # Processador com cpuinfo
    try:
        cpu_info = cpuinfo.get_cpu_info()
        info['Processador'] = cpu_info.get('brand_raw', platform.processor())
    except Exception:
        info['Processador'] = platform.processor()
    
    info['Número de Núcleos'] = psutil.cpu_count(logical=True)
    info['Memória RAM (GB)'] = round(psutil.virtual_memory().total / (1024 ** 3), 2)
    
    # Você pode converter o dicionário em string para armazenar no banco
    sistema_info = "\n".join([f"{k}: {v}" for k, v in info.items()])
    return sistema_info, info['Nome do Computador']  # usando o hostname como identificador único

# Conexão com o servidor Socket.IO
sio = socketio.Client()

# Identificador único do computador
sistema_info, username = coletar_informacoes()

@sio.event
def connect():
    print("Conectado ao servidor.")
    # Ao conectar, envia as informações do sistema
    sio.emit('registrar_usuario', {'username': username, 'sistema_info': sistema_info})

@sio.event
def disconnect():
    print("Desconectado do servidor.")

# Se quiser receber atualizações (opcional se houver uma interface web monitorando)
@sio.on('atualizar_lista')
def on_atualizar_lista(data):
    print("Lista de usuários atualizada:")
    for usuario in data.get('usuarios', []):
        print(usuario)

# Função para notificar a desconexão
def notificar_saida():
    try:
        sio.emit('usuario_desconectando', {'username': username, 'sistema_info': sistema_info})
        time.sleep(1)  # tempo para envio do evento antes de fechar
    except Exception as e:
        print("Erro ao notificar saída:", e)

# Registra a função de saída para ser chamada quando o script terminar
atexit.register(notificar_saida)

def manter_conexao():
    while True:
        # Caso deseje atualizar periodicamente as informações
        time.sleep(60)  # a cada 60 segundos (por exemplo)
        novo_info, _ = coletar_informacoes()
        # Se houver alteração ou para manter o status atualizado, emite novamente
        sio.emit('registrar_usuario', {'username': username, 'sistema_info': novo_info})

if __name__ == '__main__':
    try:
        # Conecta ao servidor (ajuste o host/porta se necessário)
        sio.connect('http://localhost:5000')
        # Cria uma thread para atualizar periodicamente (opcional)
        t = threading.Thread(target=manter_conexao, daemon=True)
        t.start()
        # Mantém o script rodando
        sio.wait()
    except Exception as e:
        print("Erro de conexão:", e)
