import platform
import socket
import psutil
import os
import cpuinfo
import socketio
import atexit
import time
import threading
import json
import sys
import re  # Adicionado para regex

nome_arquivo = 'config.json'
with open(nome_arquivo, 'r', encoding="UTF-8") as arquivo:
    dados = json.load(arquivo)

def get_anydesk_id():
    try:
        with open(r"C:\ProgramData\AnyDesk\service.conf", "r", encoding="utf-8") as f:
            content = f.read()
            # O ID geralmente aparece como "ad_id" ou "client_id"
            match = re.search(r'last_cid=(\d+)', content)
            if match:
                return match.group(1)
    except Exception as e:
        return "Desconhecido"
    return "Desconhecido"

def coletar_informacoes():
    info = {}
    info['Sistema Operacional'] = platform.system()
    info['Versão do SO'] = platform.version()
    info['Nome do SO'] = platform.platform()
    info['Arquitetura'] = platform.machine()
    
    info['Nome do Usuário'] = os.getlogin()
    info['Nome do Computador'] = socket.gethostname()
    try:
        info['Endereço IP'] = socket.gethostbyname(socket.gethostname())
    except Exception:
        info['Endereço IP'] = 'N/A'
    
    try:
        cpu_info = cpuinfo.get_cpu_info()
        info['Processador'] = cpu_info.get('brand_raw', platform.processor())
    except Exception:
        info['Processador'] = platform.processor()
    
    info['Número de Núcleos'] = psutil.cpu_count(logical=True)
    info['Memória RAM (GB)'] = round(psutil.virtual_memory().total / (1024 ** 3), 2)

    if dados["ramal"] != None:
        info["Ramal Telefone"] = dados["ramal"]

    # Adiciona o ID do AnyDesk
    info["AnyDesk ID"] = get_anydesk_id()
    
    sistema_info_str = "\n".join([f"{k}: {v}" for k, v in info.items()])
    return sistema_info_str, info['Nome do Usuário'], info

sio = socketio.Client()

sistema_info_str, username, info = coletar_informacoes()

@sio.event
def connect():
    print("Conectado ao servidor.")
    sio.emit('registrar_usuario', {'username': username, 'sistema_info_str': sistema_info_str})

@sio.event
def disconnect():
    print("Desconectado do servidor.")


def notificar_saida():
    try:
        sio.emit('usuario_desconectando', {'username': username, 'sistema_info_str': sistema_info_str})
        time.sleep(1)  
    except Exception as e:
        print("Erro ao notificar saída:", e)

atexit.register(notificar_saida)

def manter_conexao():
    while True:
        time.sleep(60)  
        novo_info, _ = coletar_informacoes()
        sio.emit('registrar_usuario', {'username': username, 'sistema_info_str': novo_info})

if __name__ == '__main__':
    try:
        sio.connect(dados["server"])
        t = threading.Thread(target=manter_conexao, daemon=True)
        t.start()
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print("Encerrando a aplicação...")
                sio.disconnect()
                sys.exit(0)
    except Exception as e:
        print("Erro de conexão:", e)
