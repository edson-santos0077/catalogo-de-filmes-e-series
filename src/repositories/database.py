import os
import sqlite3
from contextlib import contextmanager

DIRETORIO_ATUAL = os.path.dirname(__file__)
DB_PATH = os.path.abspath(os.path.join(DIRETORIO_ATUAL, "..", "..", "data", "catalogo.db"))
JSON_MIDIAS_PATH = os.path.abspath(os.path.join(DIRETORIO_ATUAL, "..", "..", "data", "catalogo.json"))
JSON_USUARIOS_PATH = os.path.abspath(os.path.join(DIRETORIO_ATUAL, "..", "..", "data", "usuarios.json"))


@contextmanager
def obter_conexao():
    """Gerenciador de contexto para conexão segura com o SQLite."""
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def inicializar_banco() -> None:
    """Cria a estrutura de tabelas SQLite caso não existam."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with obter_conexao() as conexao:
        cursor = conexao.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS midias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                tipo TEXT NOT NULL,
                genero TEXT NOT NULL,
                ano INTEGER NOT NULL,
                duracao_minutos INTEGER NOT NULL,
                classificacao TEXT,
                status TEXT NOT NULL,
                nota REAL,
                data_conclusao TEXT
            );

            CREATE TABLE IF NOT EXISTS temporadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                serie_id INTEGER NOT NULL,
                numero INTEGER NOT NULL,
                FOREIGN KEY (serie_id) REFERENCES midias(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS episodios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temporada_id INTEGER NOT NULL,
                numero_episodio INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                duracao_minutos INTEGER NOT NULL,
                status TEXT NOT NULL,
                nota REAL,
                FOREIGN KEY (temporada_id) REFERENCES temporadas(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                limite_listas INTEGER NOT NULL
            );
        """)
