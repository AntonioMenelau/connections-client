from flask import Blueprint, render_template
import sqlite3
from routes.login import login_required
from config import *

list_bp = Blueprint('list', __name__)

def obter_usuarios():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, status, info FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios

@list_bp.route('/list')
@login_required
def list_users():
    usuarios = obter_usuarios()
    return render_template('list.html', usuarios=usuarios)