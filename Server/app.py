from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, disconnect
import sqlite3
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'segredo123'
socketio = SocketIO(app)

DATABASE = 'usuarios.db'

usuarios_conectados = {}

# Funções para manipulação do banco SQLite
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def atualizar_status(username, status):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET status = ? WHERE username = ?", (status, username))
    if cursor.rowcount == 0 and username != None:
        cursor.execute("INSERT INTO usuarios (username, status) VALUES (?, ?)", (username, status))
    conn.commit()
    conn.close()

def obter_usuarios():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, status FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios

# Inicializa o banco de dados ao iniciar a aplicação
init_db()




@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado:', request.sid)

@socketio.on('registrar_usuario')
def handle_registrar_usuario(data):
    username = data.get('username')
    if not username:
        return
    atualizar_status(username, 'online')
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
    # Use threading para rodar o SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
