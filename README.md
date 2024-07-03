# server-flask-sqlite3
# Projeto de Servidor Flask com Autenticação e Gerenciamento de Arquivos
# Este projeto demonstra um simples servidor web usando Flask com recursos de registro, login e gerenciamento de arquivos.
# Estrutura do Projeto
project/
│
├── static/
│   ├── style.css
│   └── script.js
│
├── templates/
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── protected.html
│   └── edit_file.html
│
├── user-files/             # Diretório criado para armazenar os arquivos e pastas gerenciados
├── users.db
├── log.txt
├── server.py
└── README.md
# Instalação e Execução

1. **Crie e ative um ambiente virtual:**
```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate      # Windows

# pip install flask werkzeug
# python server.py
# http://127.0.0.1:5000


