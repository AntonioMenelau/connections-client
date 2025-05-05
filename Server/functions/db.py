import sqlite3
import threading
from config import *
import hashlib

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

def init_admin_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Create default admin user (username: admin, password: admin123)
    default_password = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute('INSERT OR IGNORE INTO admin (username, password) VALUES (?, ?)', 
                  ('admin', default_password))
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
