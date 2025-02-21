import platform
import socket
import psutil
import os
import cpuinfo  

def coletar_informacoes_do_computador():
    info = {}

    # Informações do Sistema Operacional
    info['Sistema Operacional'] = platform.system()
    info['Versão do SO'] = platform.version()
    info['Nome do SO'] = platform.platform()
    info['Arquitetura'] = platform.architecture()

    # Informações do Usuário
    info['Nome do Usuário'] = os.getlogin()

    # Informações do Computador
    info['Nome do Computador'] = socket.gethostname()
    info['Endereço IP'] = socket.gethostbyname(socket.gethostname())

    # Obter nome completo do processador com cpuinfo
    try:
        cpu_info = cpuinfo.get_cpu_info()
        info['Processador'] = cpu_info.get('brand_raw', platform.processor())
    except Exception as e:
        # Caso haja algum problema, usar o valor padrão do platform
        info['Processador'] = platform.processor()

    info['Número de Núcleos'] = psutil.cpu_count(logical=True)
    info['Memória RAM (GB)'] = round(psutil.virtual_memory().total / (1024 ** 3), 2)

    # Informações da Rede
    info['Interfaces de Rede'] = []
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                info['Interfaces de Rede'].append({
                    'Interface': interface,
                    'Endereço IP': addr.address,
                    'Máscara de Sub-rede': addr.netmask,
                    'Broadcast': addr.broadcast
                })

    # Impressão das informações
    print("\n=== INFORMAÇÕES DO COMPUTADOR ===\n")
    for chave, valor in info.items():
        if isinstance(valor, list):
            for item in valor:
                print(f"{chave}: {item}")
        else:
            print(f"{chave}: {valor}")

if __name__ == '__main__':
    coletar_informacoes_do_computador()