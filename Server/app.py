from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, disconnect
import sqlite3
import threading
from config import *

from routes.list_route import list_bp
from routes.principal import principal

app = Flask(__name__)
app.config['SECRET_KEY'] = 'segredo123'
socketio = SocketIO(app)


# Importando as rotas
app.register_blueprint(list_bp)
app.register_blueprint(principal)


usuarios_conectados = {}




# Funções para manipulação do banco SQLite
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            info TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def atualizar_status(username, status, info=None):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if info is None:
        cursor.execute("UPDATE usuarios SET status = ? WHERE username = ?", (status, username))
    else:
        cursor.execute("UPDATE usuarios SET status = ?, info = ? WHERE username = ?", (status, info, username))
    
    if cursor.rowcount == 0 and username is not None:
        cursor.execute("INSERT INTO usuarios (username, status, info) VALUES (?, ?, ?)", (username, status, info if info is not None else ""))
    conn.commit()
    conn.close()

def obter_usuarios():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, status, info FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios

# Inicializa o banco de dados ao iniciar a aplicação



@socketio.on('connect')
def handle_connect():
    print('Cliente conectado:', request.sid)

@socketio.on('registrar_usuario')
def handle_registrar_usuario(data):
    username = data.get('username')
    info = data.get('sistema_info_str')
    if not username:
        return
    
    # Atualizar status e info independente se é novo usuário ou reconexão
    atualizar_status(username, 'online', info)
    print(f'Usuário {username} conectado com SID {request.sid}')
    usuarios_conectados[f"{request.sid}"] = username
    usuarios = obter_usuarios()
    socketio.emit('atualizar_lista', {'usuarios': usuarios})

@socketio.on('carregarUsuarios')
def handle_disconnect():
    usuarios = obter_usuarios()
    socketio.emit('atualizar_lista', {'usuarios': usuarios})

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado:', request.sid)
    username = usuarios_conectados.get(request.sid)
    atualizar_status(username, 'offline')
    usuarios = obter_usuarios()
    socketio.emit('atualizar_lista', {'usuarios': usuarios})
    pass



if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
