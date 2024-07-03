from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import logging

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configurar logging
logging.basicConfig(filename='log.txt', level=logging.INFO)

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

    return render_template('protected.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
