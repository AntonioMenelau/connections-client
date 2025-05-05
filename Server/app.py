from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
from config import *

from routes.list_route import list_bp
from routes.login import login
from functions.db import *

import sqlite3

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

@app.route('/api/canvas/layouts')
def get_layouts():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM canvas_layouts")
    layouts = cursor.fetchall()
    conn.close()
    return jsonify([{
        'id': l[0], 
        'name': l[1], 
        'image': l[2]
    } for l in layouts])

@app.route('/api/canvas/<canvas_id>/positions')
def get_canvas_positions(canvas_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, position_x, position_y FROM canvas_positions WHERE canvas_id = ?", 
        (canvas_id,)
    )
    positions = cursor.fetchall()
    conn.close()
    return jsonify({
        'positions': [{
            'username': p[0], 
            'x': p[1], 
            'y': p[2]
        } for p in positions]
    })

@app.route('/api/canvas/position', methods=['POST'])
def save_position():
    data = request.json
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO canvas_positions 
        (username, canvas_id, position_x, position_y)
        VALUES (?, ?, ?, ?)
    """, (data['username'], data['canvas_id'], data['x'], data['y']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})


if __name__ == '__main__':    
    app.register_blueprint(list_bp)
    app.register_blueprint(login)
    
    init_db()
    init_admin_db()
    init_canvas_db()  # Add this line

    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
