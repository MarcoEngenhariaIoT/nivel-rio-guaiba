#Projeto Nível Rio Guíba App
#Eng. Marco Aurélio Machado
#marcoengenhariaiot@gmail.com
#Versão 1.0.0 27/05/2024
#Uso do código é livre desde que seja citado a minha autoria.

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import firebase_admin
from firebase_admin import credentials, db

# URL da página a ser monitorada
url = 'https://nivelguaiba.com/'

# Conectar ao banco de dados SQLite (ou criar se não existir)
conn = sqlite3.connect('nivel_agua.db')
cursor = conn.cursor()

# Criar tabela se não existir
cursor.execute('''
    CREATE TABLE IF NOT EXISTS niveis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nivel TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Inicializar o Firebase
# Crie um banco de dados no realtime database e salve o token na mesma pasta do nivel.py e substitua o caminho na linha abaixo
cred = credentials.Certificate(r'C:\Users\Marco\Dropbox\Engenharia de Software\3° Sem\Banco de dados\trabalho\guaiba-ddf2d-firebase-adminsdk-sy51j-aadec8717b.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://guaiba-ddf2d-default-rtdb.firebaseio.com'
})

# Função para extrair o nível da água
def extrair_nivel():
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    nivel = soup.find('h1').text.strip()  # Extrai o valor do nível
    return nivel

# Função para inserir o nível no banco de dados SQLite
def inserir_nivel(nivel):
    cursor.execute('INSERT INTO niveis (nivel) VALUES (?)', (nivel,))
    conn.commit()

# Função para enviar o nível ao Firebase Realtime Database
def enviar_para_firebase(nivel):
    timestamp = time.strftime('%H:%M %d-%m-%Y')
    ref = db.reference()  # Usar uma chave fixa para armazenar o valor mais recente
    ref.set({
        'nivel': ' "' + nivel + '" ',
        'timestamp': ' "' + timestamp + '" '
    })

# Inicializar o valor anterior
nivel_anterior = None

# Loop de monitoramento
while True:
    try:
        nivel_atual = extrair_nivel()
        if nivel_atual != nivel_anterior:
            inserir_nivel(nivel_atual)
            enviar_para_firebase(nivel_atual)
            nivel_anterior = nivel_atual
            print(f"Nível atualizado para {nivel_atual} e enviado para o Firebase")
        else:
            print(f"Nível permanece em {nivel_atual}")
    except Exception as e:
        print(f"Erro ao obter o nível da água: {e}")

    # Esperar por um tempo antes de verificar novamente (por exemplo, a cada 15 minutos)
    time.sleep(900)

# Fechar a conexão com o banco de dados (em um caso real, você pode precisar de um encerramento mais elegante)
conn.close()
