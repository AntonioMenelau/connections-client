from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, disconnect
from config import *

from routes.list_route import list_bp
from routes.login import login
from functions.db import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nexus1234$'
socketio = SocketIO(app)

usuarios_conectados = {}



@socketio.on('connect')
def handle_connect():
    print('Cliente conectado:', request.sid)

@socketio.on('registrar_usuario')
def handle_registrar_usuario(data):
    username = data.get('username')
    info = data.get('sistema_info_str')
    if not username:
        return
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
    app.register_blueprint(list_bp)
    app.register_blueprint(login)

    
    init_db()
    init_admin_db()


    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
