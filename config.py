import os
import sys
import sqlite3
import configparser  # Importar o configparser
import json



# 📄 config.py
VERSAO_ATUAL = "1.0.1"  # Sempre atualize esta versão quando fizer novo release
REPO_URL = "https://api.github.com/repos/Ruitervanderley/pomodoro-timer-app"
CHAVE_PUBLICA_PATH = "assets/public_key.pem"

def resource_path(relative_path):
    """Obtenha o caminho absoluto para o arquivo de recurso, considerando se está rodando em modo dev ou como um executável."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Inicializa o configparser
config = configparser.ConfigParser()
if os.path.exists('config.ini'):
    config.read('config.ini')
else:
    print("Warning: 'config.ini' file not found. Using default values.")

# Obter as configurações da seção 'DEFAULT' ou definir valores padrão
RUTA_LOGO = resource_path(config['DEFAULT'].get('RUTA_LOGO', 'assets/logo.png')) if 'DEFAULT' in config else resource_path('assets/logo.png')
RUTA_START_SOUND = resource_path(config['DEFAULT'].get('RUTA_START_SOUND', 'assets/start_sound.wav')) if 'DEFAULT' in config else resource_path('assets/start_sound.wav')
RUTA_ALERT_SOUND = resource_path(config['DEFAULT'].get('RUTA_ALERT_SOUND', 'assets/alert_sound.wav')) if 'DEFAULT' in config else resource_path('assets/alert_sound.wav')
RUTA_END_SOUND = resource_path(config['DEFAULT'].get('RUTA_END_SOUND', 'assets/end_sound.wav')) if 'DEFAULT' in config else resource_path('assets/end_sound.wav')

# Configurações do aplicativo
TEMA = config['DEFAULT'].get('TEMA', 'Claro') if 'DEFAULT' in config else 'Claro'


# Configuração do banco de dados SQLite
DATABASE_PATH = resource_path("database.db")

# Função para criar o banco de dados e a tabela de usuários se não existirem
def initialize_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Criação da tabela de usuários (se não existir)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            senha TEXT NOT NULL,
            admin INTEGER DEFAULT 0,  -- Adiciona a coluna admin para verificar privilégios
            data_expiracao TEXT,
            serial TEXT  -- Adiciona a coluna serial para gerenciar a ativação da licença
        )
    ''')

    # Verificação e adição das colunas admin, data_expiracao, e serial (se não existirem)
    cursor.execute("PRAGMA table_info(usuarios)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "admin" not in columns:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN admin INTEGER DEFAULT 0")

    if "data_expiracao" not in columns:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN data_expiracao TEXT")

    if "serial" not in columns:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN serial TEXT")
    
    conn.commit()
    conn.close()

# Chamar a função de inicialização do banco de dados ao importar o config
initialize_database()

CONFIG_FILE = "config.json"

def salvar_configuracao(chave, valor):
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}
    
    config[chave] = valor
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def carregar_configuracao(chave, padrao=None):
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return config.get(chave, padrao)
    except FileNotFoundError:
        return padrao

TAMANHO_CRONOMETRO = 200  # Defina o tamanho do cronômetro conforme necessário
