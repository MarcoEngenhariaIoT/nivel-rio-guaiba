#Projeto Nível Rio Guíba App
#Eng. Marco Aurélio Machado
#marcoengenhariaiot@gmail.com
#Uso do código é livre desde que seja citado a minha autoria.
#Versão 1.0.0 27/05/2024 
    #Versão inicial
#Versão 1.0.1 28/05/2024 
    #Alterado o formado do envio do valor do nível de string para decimal e sem o "m" 
#Versão 1.1.0 05/06/2024 
    #Incluido o envio de msg do APP para os Labels pois podem mudar esses parâmetros
    #Incluido as variáveis de cota de alerta e inundação.
    #Com essas mudanças não é necessário alterar esses paâmetros no aplicativo, se muda apenas nesse código.

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import firebase_admin
from firebase_admin import credentials, db

#valores das cotas
cotaAlerta = 3.15
cotaInundacao = 3.60
print("Cota de alerta :", cotaAlerta)
print("Cota de inundação :", cotaInundacao)

# Mensagens do APP
labelVersao = "Versão 1.1.0"
labelCotaAlerta = "Cota de alerta 3.15m"
labelCotaInundacao = "Cota de inundação 3.60m"
labelEstacao = "Estação: Cais Mauá C6 / Gasômetro"
labelFree = "Aplicativo experimental de uso livre sem fins lucrativos, os dados coletados podem conter erros e não nos responsabilizamos pelo mau uso dessas informações, para tomada de decisão recomendamos consultar diretamente a fonte confiável com o SNIRH/ANA."

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
    nivel = converter_string_para_decimal(nivel)
    return nivel

# Função para converter de string para decimal
def converter_string_para_decimal(string):
    string = string.replace(" m", "")
    string = string.replace(",", ".")
    valor_decimal = float(string)    
    return valor_decimal

# Função para inserir o nível no banco de dados SQLite
def inserir_nivel(nivel):
    cursor.execute('INSERT INTO niveis (nivel) VALUES (?)', (nivel,))
    conn.commit()

# Função para enviar o nível ao Firebase Realtime Database
def enviar_para_firebase(nivel):
    timestamp = time.strftime('%H:%M %d-%m-%Y')
    ref = db.reference()  # Usar uma chave fixa para armazenar o valor mais recente
    ref.set({
        'nivel': nivel,
        'timestamp': ' "' + timestamp + '" ',
        'labelVersao': ' "' + labelVersao + '" ',
        'labelCotaAlerta': ' "' + labelCotaAlerta + '" ',
        'labelCotaInundacao': ' "' + labelCotaInundacao + '" ',
        'labelEstacao': ' "' + labelEstacao + '" ',
        'labelFree': ' "' + labelFree + '" ',
        'gAlerta': cotaAlerta,
        'gInundacao': cotaInundacao
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

# Fechar a conexão com o banco de dados
conn.close()
