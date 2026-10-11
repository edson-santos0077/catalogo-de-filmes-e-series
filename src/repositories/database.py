import sqlite3
import os

# Define o caminho do banco de dados na raiz do projeto (ou em uma pasta específica, como /data)
# 1. Pega o diretório atual onde está o arquivo database.py (src/repositories/)
DIRETORIO_ATUAL = os.path.dirname(__file__)

# 2. Constrói o caminho: sobe para src (..), sobe para a raiz (..), entra em data e aponta para catalogo.db
DB_PATH = os.path.join(DIRETORIO_ATUAL, '..', '..', 'data', 'catalogo.db')

# 3. Resolve o caminho para ficar limpo (remove os ".." e normaliza o caminho absoluto)
DB_PATH = os.path.abspath(DB_PATH)

def obter_conexao():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    conexao = sqlite3.connect(DB_PATH)
    # Permite acessar os resultados como dicionários em vez de tuplas numéricas
    conexao.row_factory = sqlite3.Row
    return conexao

def inicializar_banco():

    # Cria a pasta 'data' automaticamente caso ela não exista
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    banco_ja_existe = os.path.exists(DB_PATH)

    # Verifica se o arquivo já existe antes de tentar criar as tabelas
    banco_ja_existe = os.path.exists(DB_PATH)


    if banco_ja_existe: # Se já existe, não precisa criar o db
        return

    #Cria as tabelas necessárias se elas não existirem
    conexao = obter_conexao()
    cursor = conexao.cursor()

    # Exemplo: Criação da tabela de mídias (Filmes e Séries)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS midias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            tipo TEXT NOT NULL,
            genero TEXT,
            ano INTEGER,
            duracao_minutos INTEGER,
            classificacao TEXT,
            status TEXT,
            nota REAL,
            data_conclusao TEXT
        )
    ''')

    # Você adicionaria outros CREATE TABLE aqui (ex: episodios, usuarios, listas)

    conexao.commit()
    conexao.close()

# Executa a inicialização ao importar o módulo, garantindo que o banco exista
inicializar_banco()
