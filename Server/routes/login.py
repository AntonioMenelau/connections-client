from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
from config import *
from functions.db import *
from functools import wraps
import hashlib

login = Blueprint('login', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash('Faça login para continuar', 'warning')
            return redirect(url_for('login.login_page'))
        return f(*args, **kwargs)
    return decorated_function

@login.route('/login', methods=['GET', 'POST'])
def login_page():
    # Redirect if already logged in
    if session.get('admin'):
        return redirect(url_for('login.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username and password:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute('SELECT * FROM admin WHERE username = ? AND password = ?', 
                         (username, hashed_password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['admin'] = True
                session['username'] = username
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('login.index'))
            else:
                flash('Credenciais inválidas!', 'error')
        else:
            flash('Por favor, preencha todos os campos!', 'warning')
            
    return render_template('login.html')

@login.route('/logout')
@login_required
def logout():
    username = session.get('username')
    session.clear()
    flash(f'Logout realizado com sucesso!', 'success')
    return redirect(url_for('login.login_page'))

@login.route('/')
@login_required
def index():
    return render_template('canvas.html', username=session.get('username'))

# Adicione uma rota para alterar senha
@login.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            flash('Preencha todos os campos!', 'warning')
            return redirect(url_for('login.change_password'))
            
        if new_password != confirm_password:
            flash('As senhas não coincidem!', 'error')
            return redirect(url_for('login.change_password'))
            
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Verify current password
        current_hashed = hashlib.sha256(current_password.encode()).hexdigest()
        cursor.execute('SELECT * FROM admin WHERE username = ? AND password = ?',
                      (session['username'], current_hashed))
        
        if cursor.fetchone():
            # Update password
            new_hashed = hashlib.sha256(new_password.encode()).hexdigest()
            cursor.execute('UPDATE admin SET password = ? WHERE username = ?',
                         (new_hashed, session['username']))
            conn.commit()
            flash('Senha alterada com sucesso!', 'success')
        else:
            flash('Senha atual incorreta!', 'error')
            
        conn.close()
        return redirect(url_for('login.index'))
        
    return render_template('change_password.html')
