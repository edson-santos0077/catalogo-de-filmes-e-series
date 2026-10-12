import json
import os
import sqlite3
from abc import ABC, abstractmethod

from models import Episodio, Filme, Serie, Temporada

# --- 1. CONFIGURAÇÃO DE CAMINHOS ---
DIRETORIO_ATUAL = os.path.dirname(__file__)
DB_PATH = os.path.abspath(
    os.path.join(DIRETORIO_ATUAL, "..", "..", "data", "catalogo.db")
)
JSON_PATH = os.path.abspath(
    os.path.join(DIRETORIO_ATUAL, "..", "..", "data", "catalogo.json")
)


# --- 2. FUNÇÕES AUXILIARES SQLITE ---
def obter_conexao():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        return
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("""
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
    """)
    conexao.commit()
    conexao.close()


# --- 3. CONTRATO (INTERFACE) ---
class MidiaRepository(ABC):
    """Interface base para repositórios de mídia."""

    @abstractmethod
    def salvar_todos(self, midias: list) -> None:
        pass

    @abstractmethod
    def carregar_todos(self) -> list:
        pass


# --- 4. IMPLEMENTAÇÃO JSON ---
class MidiaRepositoryJSON(MidiaRepository):
    """Repositório persistindo em arquivo .json"""

    def __init__(self):
        self.caminho = JSON_PATH
        os.makedirs(os.path.dirname(self.caminho), exist_ok=True)

    def salvar_todos(self, midias: list) -> None:
        dados_completos = []
        for midia in midias:
            dict_midia = midia.to_dict()
            if isinstance(midia, Serie):
                dict_midia["temporadas"] = []
                for temporada in midia.temporadas:
                    dict_temp = temporada.to_dict()
                    dict_temp["episodios"] = [
                        ep.to_dict() for ep in temporada.episodios
                    ]
                    dict_midia["temporadas"].append(dict_temp)
            dados_completos.append(dict_midia)

        with open(self.caminho, "w", encoding="utf-8") as f:
            json.dump(dados_completos, f, indent=4, ensure_ascii=False)

    def carregar_todos(self) -> list:
        if not os.path.exists(self.caminho):
            return []

        with open(self.caminho, "r", encoding="utf-8") as f:
            try:
                dados_brutos = json.load(f)
            except json.JSONDecodeError:
                return []

        midias_carregadas = []
        for dados in dados_brutos:
            tipo = dados.get("tipo")
            if tipo == "FILME":
                midias_carregadas.append(Filme.from_dict(dados))
            elif tipo == "SERIE":
                dados_temporadas = dados.pop("temporadas", [])
                serie = Serie.from_dict(dados)
                for dados_temp in dados_temporadas:
                    dados_episodios = dados_temp.pop("episodios", [])
                    temporada = Temporada.from_dict(dados_temp)
                    for dados_ep in dados_episodios:
                        temporada.adicionar_episodio(Episodio.from_dict(dados_ep))
                    serie.adicionar_temporada(temporada)
                midias_carregadas.append(serie)

        return midias_carregadas


# --- 5. IMPLEMENTAÇÃO SQLITE ---
class MidiaRepositorySQLite(MidiaRepository):
    """Repositório persistindo em banco relacional .db"""

    def __init__(self):
        inicializar_banco()

    def salvar_todos(self, midias: list) -> None:
        # A implementar nas próximas semanas (DELETE inicial + INSERTs)
        pass

    def carregar_todos(self) -> list:
        # A implementar nas próximas semanas (SELECTs com JOIN)
        return []
