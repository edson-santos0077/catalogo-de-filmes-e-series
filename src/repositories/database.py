import json
import os
import sqlite3
from abc import ABC, abstractmethod
from contextlib import contextmanager

from models.enums import TipoMidia
from models.filme import Filme
from models.midia import Midia
from models.serie import Episodio, Serie, Temporada

# --- 1. CONFIGURAÇÃO DE CAMINHOS ---
DIRETORIO_ATUAL = os.path.dirname(__file__)
DB_PATH = os.path.abspath(
    os.path.join(DIRETORIO_ATUAL, "..", "..", "data", "catalogo.db")
)
JSON_PATH = os.path.abspath(
    os.path.join(DIRETORIO_ATUAL, "..", "..", "data", "catalogo.json")
)


# --- 2. GERENCIADOR DE CONEXÃO COM DECORADOR ---
@contextmanager
def obter_conexao():
    """Gerenciador de contexto para conexão com o SQLite."""
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
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with obter_conexao() as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
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
            )
        """)


# --- 3. CONTRATO (INTERFACE) ---
class MidiaRepository(ABC):
    """Interface base para repositórios de mídia."""

    @abstractmethod
    def salvar_todos(self, midias: list[Midia]) -> None:
        pass

    @abstractmethod
    def carregar_todos(self) -> list[Midia]:
        pass


# --- 4. IMPLEMENTAÇÃO JSON ---
class MidiaRepositoryJSON(MidiaRepository):
    """Repositório persistindo em arquivo .json"""

    def __init__(self):
        self.caminho = JSON_PATH
        os.makedirs(os.path.dirname(self.caminho), exist_ok=True)

    @staticmethod
    def _obter_proximo_id(midias: list[Midia]) -> int:
        ids_existentes = [m.id for m in midias if m.id is not None]
        return (max(ids_existentes) + 1) if ids_existentes else 1

    def salvar_todos(self, midias: list[Midia]) -> None:
        proximo_id = self._obter_proximo_id(midias)

        # Atribuição dos IDs em memória para mídias novas
        for midia in midias:
            if midia.id is None:
                midia.id = proximo_id
                proximo_id += 1

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

    def carregar_todos(self) -> list[Midia]:
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
            if tipo == TipoMidia.FILME.value:
                midias_carregadas.append(Filme.from_dict(dados))
            elif tipo == TipoMidia.SERIE.value:
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

    def salvar_todos(self, midias: list[Midia]) -> None:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()

            for midia in midias:
                nota_valor = midia.nota
                data_conclusao_str = (
                    midia.data_conclusao.isoformat() if midia.data_conclusao else None
                )

                if midia.id is None:
                    cursor.execute(
                        """
                        INSERT INTO midias (titulo, tipo, genero, ano, duracao_minutos, classificacao, status, nota, data_conclusao)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            midia.titulo,
                            midia.tipo.value,
                            midia.genero,
                            midia.ano,
                            midia.duracao_minutos,
                            midia.classificacao_indicativa,
                            midia.status.value,
                            nota_valor,
                            data_conclusao_str,
                        ),
                    )
                    midia.id = cursor.lastrowid
                else:
                    cursor.execute(
                        """
                        UPDATE midias
                        SET titulo=?, tipo=?, genero=?, ano=?, duracao_minutos=?, classificacao=?, status=?, nota=?, data_conclusao=?
                        WHERE id=?
                        """,
                        (
                            midia.titulo,
                            midia.tipo.value,
                            midia.genero,
                            midia.ano,
                            midia.duracao_minutos,
                            midia.classificacao_indicativa,
                            midia.status.value,
                            nota_valor,
                            data_conclusao_str,
                            midia.id,
                        ),
                    )

    def carregar_todos(self) -> list[Midia]:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM midias")
            linhas = cursor.fetchall()

            midias = []
            for linha in linhas:
                dados = dict(linha)
                tipo = dados.get("tipo")

                if tipo == TipoMidia.FILME.value:
                    midias.append(
                        Filme(
                            id=dados["id"],
                            titulo=dados["titulo"],
                            genero=dados["genero"],
                            ano=dados["ano"],
                            duracao_minutos=dados["duracao_minutos"],
                            classificacao_indicativa=dados["classificacao"],
                        )
                    )
                elif tipo == TipoMidia.SERIE.value:
                    midias.append(
                        Serie(
                            id=dados["id"],
                            titulo=dados["titulo"],
                            genero=dados["genero"],
                            ano=dados["ano"],
                            classificacao_indicativa=dados["classificacao"],
                        )
                    )

            return midias
