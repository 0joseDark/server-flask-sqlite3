from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
import logging

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configurar logging
logging.basicConfig(filename='log.txt', level=logging.INFO)

# Diretório para arquivos
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FILES_DIR = os.path.join(BASE_DIR, 'user-files')
os.makedirs(FILES_DIR, exist_ok=True)

# Conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Criar tabela de usuários se não existir
def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            username TEXT NOT NULL UNIQUE,
                            email TEXT NOT NULL,
                            password TEXT NOT NULL
                        );''')
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        try:
            with conn:
                conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
            flash('Registration successful! You can now log in.', 'success')
            logging.info(f'User {username} registered successfully.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'danger')
            logging.warning(f'Registration failed for user {username} due to duplicate entry.')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            logging.info(f'User {username} logged in successfully.')
            return redirect(url_for('protected'))
        else:
            flash('Invalid username or password.', 'danger')
            logging.warning(f'Failed login attempt for user {username}.')

    return render_template('login.html')

@app.route('/protected')
def protected():
    if 'user_id' not in session:
        flash('You need to be logged in to access this page.', 'warning')
        return redirect(url_for('login'))

    items = []
    for root, dirs, files in os.walk(FILES_DIR):
        for d in dirs:
            items.append(os.path.relpath(os.path.join(root, d), FILES_DIR))
        for f in files:
            items.append(os.path.relpath(os.path.join(root, f), FILES_DIR))

    return render_template('protected.html', items=items)

@app.route('/add_folder', methods=['POST'])
def add_folder():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    folder_name = request.form['folder_name']
    if folder_name:
        new_folder_path = os.path.join(FILES_DIR, folder_name)
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
            flash('Folder created successfully!', 'success')
            logging.info(f'Folder "{folder_name}" created.')
        else:
            flash('Folder already exists.', 'warning')

    return redirect(url_for('protected'))

@app.route('/edit_file/<path:filename>', methods=['GET', 'POST'])
def edit_file(filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    file_path = os.path.join(FILES_DIR, filename)
    
    if os.path.isdir(file_path):
        flash('Cannot edit a folder. Please select a file.', 'warning')
        return redirect(url_for('protected'))
    
    if request.method == 'POST':
        content = request.form['content']
        with open(file_path, 'w') as f:
            f.write(content)
        flash('File updated successfully!', 'success')
        logging.info(f'File "{filename}" edited.')
        return redirect(url_for('protected'))

    if not os.path.isfile(file_path):
        flash('File does not exist.', 'danger')
        return redirect(url_for('protected'))

    with open(file_path, 'r') as f:
        content = f.read()

    return render_template('edit_file.html', filename=filename, content=content)

@app.route('/delete_item/<path:filename>')
def delete_item(filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    file_path = os.path.join(FILES_DIR, filename)
    
    if not os.path.exists(file_path):
        flash('Item does not exist.', 'danger')
        return redirect(url_for('protected'))

    try:
        if os.path.isdir(file_path):
            os.rmdir(file_path)
        else:
            os.remove(file_path)
        flash('Item deleted successfully!', 'success')
        logging.info(f'Item "{filename}" deleted.')
    except OSError as e:
        flash(f'Error deleting item: {e}', 'danger')
        logging.error(f'Error deleting item "{filename}": {e}')

    return redirect(url_for('protected'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
