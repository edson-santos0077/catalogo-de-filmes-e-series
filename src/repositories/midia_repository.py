import json
import os
from abc import ABC, abstractmethod

from src.models.enums import StatusVisualizacao, TipoMidia
from src.models.filme import Filme
from src.models.midia import Midia
from src.models.serie import Episodio, Serie, Temporada
from src.repositories.database import JSON_MIDIAS_PATH, inicializar_banco, obter_conexao


class MidiaRepository(ABC):
    """Interface abstrata (Contrato) para o repositório de mídias."""

    @abstractmethod
    def salvar_todos(self, midias: list[Midia]) -> None:
        pass

    @abstractmethod
    def carregar_todos(self) -> list[Midia]:
        pass


class MidiaRepositoryJSON(MidiaRepository):
    """Repositório de mídias persistindo em JSON."""

    def __init__(self, caminho: str = JSON_MIDIAS_PATH):
        self.caminho = caminho
        os.makedirs(os.path.dirname(self.caminho), exist_ok=True)

    def _obter_proximo_id(self, midias: list[Midia]) -> int:
        ids_existentes = [m.id for m in midias if m.id is not None]
        return (max(ids_existentes) + 1) if ids_existentes else 1

    def salvar_todos(self, midias: list[Midia]) -> None:
        proximo_id = self._obter_proximo_id(midias)

        for midia in midias:
            if midia.id is None:
                midia.id = proximo_id
                proximo_id += 1

        dados_completos = [midia.to_dict() for midia in midias]

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
                filme = Filme.from_dict(dados)
                if dados.get("status"):
                    filme.alterar_status(StatusVisualizacao(dados["status"]))
                if dados.get("nota") is not None:
                    filme.nota = dados["nota"]
                if dados.get("data_conclusao"):
                    filme.data_conclusao = dados["data_conclusao"]
                midias_carregadas.append(filme)

            elif tipo == TipoMidia.SERIE.value:
                dados_temporadas = dados.pop("temporadas", [])
                serie = Serie.from_dict(dados)

                for dados_temp in dados_temporadas:
                    dados_episodios = dados_temp.pop("episodios", [])
                    temporada = Temporada.from_dict(dados_temp)
                    for dados_ep in dados_episodios:
                        ep = Episodio.from_dict(dados_ep)
                        if dados_ep.get("status"):
                            ep.alterar_status(StatusVisualizacao(dados_ep["status"]))
                        if dados_ep.get("nota") is not None:
                            ep.nota = dados_ep["nota"]
                        temporada.adicionar_episodio(ep)
                    serie.adicionar_temporada(temporada)

                if dados.get("status"):
                    serie.alterar_status(StatusVisualizacao(dados["status"]))
                if dados.get("data_conclusao"):
                    serie.data_conclusao = dados["data_conclusao"]

                midias_carregadas.append(serie)

        return midias_carregadas


class MidiaRepositorySQLite(MidiaRepository):
    """Repositório de mídias persistindo em SQLite."""

    def __init__(self):
        inicializar_banco()

    def salvar_todos(self, midias: list[Midia]) -> None:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            for midia in midias:
                nota_valor = midia.nota
                data_conclusao_str = midia.data_conclusao.isoformat() if midia.data_conclusao else None

                # 1. Salvar a Mídia Base
                if midia.id is None:
                    cursor.execute(
                        """INSERT INTO midias (titulo, tipo, genero, ano, duracao_minutos, classificacao, status, nota, data_conclusao)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (midia.titulo, midia.tipo.value, midia.genero, midia.ano, midia.duracao_minutos,
                         midia.classificacao_indicativa, midia.status.value, nota_valor, data_conclusao_str)
                    )
                    midia.id = cursor.lastrowid
                else:
                    cursor.execute(
                        """UPDATE midias SET titulo=?, tipo=?, genero=?, ano=?, duracao_minutos=?, classificacao=?, status=?, nota=?, data_conclusao=?
                           WHERE id=?""",
                        (midia.titulo, midia.tipo.value, midia.genero, midia.ano, midia.duracao_minutos,
                         midia.classificacao_indicativa, midia.status.value, nota_valor, data_conclusao_str, midia.id)
                    )

                # 2. Se for Série, salvar a hierarquia de Temporadas e Episódios
                if midia.tipo == TipoMidia.SERIE:
                    # Estratégia simples: limpar as temporadas antigas e recriar (aproveitando o ON DELETE CASCADE)
                    cursor.execute("DELETE FROM temporadas WHERE serie_id = ?", (midia.id,))

                    for temporada in midia.temporadas:
                        cursor.execute(
                            "INSERT INTO temporadas (serie_id, numero) VALUES (?, ?)",
                            (midia.id, temporada.numero)
                        )
                        temporada_id = cursor.lastrowid

                        for ep in temporada.episodios:
                            cursor.execute(
                                """INSERT INTO episodios (temporada_id, numero_episodio, titulo, duracao_minutos, status, nota)
                                   VALUES (?, ?, ?, ?, ?, ?)""",
                                (temporada_id, ep.numero_episodio, ep.titulo, ep.duracao_minutos, ep.status.value, ep.nota)
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
                    filme = Filme(
                        id=dados["id"],
                        titulo=dados["titulo"],
                        genero=dados["genero"],
                        ano=dados["ano"],
                        duracao_minutos=dados["duracao_minutos"],
                        classificacao_indicativa=dados["classificacao"],
                    )
                    if dados["status"]:
                        filme.alterar_status(StatusVisualizacao(dados["status"]))
                    if dados["nota"] is not None:
                        filme.nota = dados["nota"]
                    if dados["data_conclusao"]:
                        filme.data_conclusao = dados["data_conclusao"]
                    midias.append(filme)

                elif tipo == TipoMidia.SERIE.value:
                    serie = Serie(
                        id=dados["id"],
                        titulo=dados["titulo"],
                        genero=dados["genero"],
                        ano=dados["ano"],
                        classificacao_indicativa=dados["classificacao"],
                    )
                    if dados["status"]:
                        serie.alterar_status(StatusVisualizacao(dados["status"]))
                    if dados["data_conclusao"]:
                        serie.data_conclusao = dados["data_conclusao"]

                    # --- CORREÇÃO: Buscar as temporadas desta série ---
                    cursor.execute("SELECT * FROM temporadas WHERE serie_id = ?", (serie.id,))
                    temporadas_db = cursor.fetchall()

                    for temp_db in temporadas_db:
                        temporada = Temporada(numero=temp_db["numero"])

                        # Buscar os episódios desta temporada
                        cursor.execute("SELECT * FROM episodios WHERE temporada_id = ?", (temp_db["id"],))
                        episodios_db = cursor.fetchall()

                        for ep_db in episodios_db:
                            ep = Episodio(
                                numero_temporada=temporada.numero,
                                numero_episodio=ep_db["numero_episodio"],
                                titulo=ep_db["titulo"],
                                duracao_minutos=ep_db["duracao_minutos"]
                            )
                            if ep_db["status"]:
                                ep.alterar_status(StatusVisualizacao(ep_db["status"]))
                            if ep_db["nota"] is not None:
                                ep.nota = ep_db["nota"]

                            temporada.adicionar_episodio(ep)

                        serie.adicionar_temporada(temporada)

                    midias.append(serie)

            return midias
