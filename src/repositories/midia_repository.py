import json
import os
from abc import ABC, abstractmethod

from src.models.enums import StatusVisualizacao
from src.models.filme import Filme
from src.models.midia import Midia
from src.models.serie import Episodio, Serie, Temporada
from src.repositories.database import JSON_MIDIAS_PATH, inicializar_banco, obter_conexao


def _normalizar_tipo(tipo_val) -> str:
    """Padroniza a identificação do tipo de mídia ignorando acentos e variação de caixa."""
    if hasattr(tipo_val, "value"):
        tipo_val = tipo_val.value
    s = str(tipo_val or "").strip().upper()
    if "SERI" in s or "SÉR" in s:
        return "SERIE"
    if "FILM" in s:
        return "FILME"
    return s


def _obter_id_midia(objeto: Midia) -> int | None:
    """Recupera o ID da mídia tratando propriedades, métodos getter e atributos privados."""
    if objeto is None:
        return None

    val = getattr(objeto, "id", None)
    if callable(val):
        try:
            val = val()
        except Exception:
            val = None

    if val is None:
        val = getattr(objeto, "_id", None)
        if callable(val):
            try:
                val = val()
            except Exception:
                val = None

    if val is not None:
        try:
            return int(val)
        except (ValueError, TypeError):
            pass

    return None


def _definir_id_seguro(objeto: Midia, midia_id: int) -> None:
    """Atribui o ID na instância independente do encapsulamento do modelo."""
    if objeto is None:
        return
    objeto._id = midia_id
    try:
        setattr(objeto, "id", midia_id)
    except Exception:
        pass


def _restaurar_status_silencioso(objeto: Midia, status_val: str) -> None:
    """Restaura o status diretamente sem disparar eventos durante a desserialização."""
    if not status_val:
        return
    try:
        status_enum = StatusVisualizacao(status_val) if isinstance(status_val, str) else status_val
        objeto._status = status_enum
    except Exception:
        pass


class MidiaRepository(ABC):
    """Interface abstrata (Contrato) para o repositório de mídias."""

    @abstractmethod
    def salvar_todos(self, midias: list[Midia]) -> None:
        pass

    @abstractmethod
    def carregar_todos(self) -> list[Midia]:
        pass

    @abstractmethod
    def adicionar(self, midia: Midia) -> Midia:
        pass

    @abstractmethod
    def atualizar(self, midia: Midia) -> None:
        pass

    @abstractmethod
    def listar_todas(self) -> list[Midia]:
        pass

    @abstractmethod
    def obter_por_id(self, midia_id: int) -> Midia | None:
        pass


class MidiaRepositoryJSON(MidiaRepository):
    """Repositório de mídias persistindo em JSON."""

    def __init__(self, caminho: str = JSON_MIDIAS_PATH):
        self.caminho = caminho
        os.makedirs(os.path.dirname(self.caminho), exist_ok=True)

    def _obter_proximo_id(self, midias: list[Midia]) -> int:
        ids = [_obter_id_midia(m) for m in midias if _obter_id_midia(m) is not None]
        return (max(ids) + 1) if ids else 1

    def salvar_todos(self, midias: list[Midia]) -> None:
        proximo_id = self._obter_proximo_id(midias)

        for midia in midias:
            if _obter_id_midia(midia) is None:
                _definir_id_seguro(midia, proximo_id)
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
        for dados_item in dados_brutos:
            try:
                dados = dict(dados_item)

                tipo_bruto = dados.get("tipo") or dados.get("_tipo")
                tipo_norm = _normalizar_tipo(tipo_bruto)
                midia_id = dados.get("id") if dados.get("id") is not None else dados.get("_id")
                status_bruto = dados.get("status") or dados.get("_status")

                if tipo_norm == "FILME":
                    filme = Filme.from_dict(dados)
                    if midia_id is not None:
                        _definir_id_seguro(filme, midia_id)
                    _restaurar_status_silencioso(filme, status_bruto)
                    midias_carregadas.append(filme)

                elif tipo_norm == "SERIE":
                    dados_temporadas = dados.pop("temporadas", [])
                    serie = Serie.from_dict(dados)
                    if midia_id is not None:
                        _definir_id_seguro(serie, midia_id)

                    for dados_temp in dados_temporadas:
                        dados_episodios = dados_temp.pop("episodios", [])
                        temporada = Temporada.from_dict(dados_temp)
                        for dados_ep in dados_episodios:
                            ep = Episodio.from_dict(dados_ep)
                            ep_status = dados_ep.get("status") or dados_ep.get("_status")
                            _restaurar_status_silencioso(ep, ep_status)
                            temporada.adicionar_episodio(ep)
                        serie.adicionar_temporada(temporada)

                    _restaurar_status_silencioso(serie, status_bruto)
                    midias_carregadas.append(serie)
            except Exception:
                continue

        return midias_carregadas

    def listar_todas(self) -> list[Midia]:
        return self.carregar_todos()

    def obter_por_id(self, midia_id: int) -> Midia | None:
        return next((m for m in self.carregar_todos() if _obter_id_midia(m) == midia_id), None)

    def adicionar(self, midia: Midia) -> Midia:
        midias = self.carregar_todos()
        midias.append(midia)
        self.salvar_todos(midias)
        return midia

    def atualizar(self, midia: Midia) -> None:
        midias = self.carregar_todos()
        midia_id_alvo = _obter_id_midia(midia)
        for i, m in enumerate(midias):
            if _obter_id_midia(m) == midia_id_alvo:
                midias[i] = midia
                break
        self.salvar_todos(midias)


class MidiaRepositorySQLite(MidiaRepository):
    """Repositório de mídias persistindo em SQLite."""

    def __init__(self):
        inicializar_banco()

    def _converter_linha_para_midia(self, conexao, linha) -> Midia | None:
        dados = dict(linha)
        tipo_norm = _normalizar_tipo(dados.get("tipo"))
        midia_id = dados.get("id")

        if tipo_norm == "FILME":
            filme = Filme(
                titulo=dados.get("titulo") or "",
                genero=dados.get("genero") or "",
                ano=dados.get("ano") or 0,
                duracao_minutos=dados.get("duracao_minutos") or 0,
                classificacao_indicativa=dados.get("classificacao") or "Livre",
            )
            _definir_id_seguro(filme, midia_id)
            _restaurar_status_silencioso(filme, dados.get("status"))
            if dados.get("nota") is not None:
                filme.nota = dados["nota"]
            if dados.get("data_conclusao"):
                filme.data_conclusao = dados["data_conclusao"]
            return filme

        elif tipo_norm == "SERIE":
            serie = Serie(
                titulo=dados.get("titulo") or "",
                genero=dados.get("genero") or "",
                ano=dados.get("ano") or 0,
                classificacao_indicativa=dados.get("classificacao") or "Livre",
            )
            _definir_id_seguro(serie, midia_id)
            _restaurar_status_silencioso(serie, dados.get("status"))

            if dados.get("data_conclusao"):
                serie.data_conclusao = dados["data_conclusao"]

            cursor_temp = conexao.cursor()
            cursor_temp.execute(
                "SELECT * FROM temporadas WHERE serie_id = ?", (midia_id,)
            )
            temporadas_db = cursor_temp.fetchall()

            for temp_db in temporadas_db:
                temporada = Temporada(numero=temp_db["numero"])

                cursor_ep = conexao.cursor()
                cursor_ep.execute(
                    "SELECT * FROM episodios WHERE temporada_id = ?",
                    (temp_db["id"],),
                )
                episodios_db = cursor_ep.fetchall()

                for ep_db in episodios_db:
                    ep = Episodio(
                        numero_temporada=temporada.numero,
                        numero_episodio=ep_db["numero_episodio"],
                        titulo=ep_db["titulo"],
                        duracao_minutos=ep_db["duracao_minutos"],
                    )
                    _restaurar_status_silencioso(ep, ep_db.get("status"))
                    if ep_db.get("nota") is not None:
                        ep.nota = ep_db["nota"]

                    temporada.adicionar_episodio(ep)

                serie.adicionar_temporada(temporada)

            return serie

        return None

    def salvar_todos(self, midias: list[Midia]) -> None:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            for midia in midias:
                m_id = _obter_id_midia(midia)
                m_titulo = getattr(midia, "titulo", getattr(midia, "_titulo", ""))
                m_tipo = getattr(midia, "tipo", getattr(midia, "_tipo", ""))
                m_genero = getattr(midia, "genero", getattr(midia, "_genero", ""))
                m_ano = getattr(midia, "ano", getattr(midia, "_ano", 0))
                m_classificacao = getattr(midia, "classificacao_indicativa", getattr(midia, "_classificacao_indicativa", ""))
                m_status = getattr(midia, "status", getattr(midia, "_status", StatusVisualizacao.NAO_ASSISTIDO))
                status_str = m_status.value if hasattr(m_status, "value") else str(m_status)

                nota_valor = getattr(midia, "nota", getattr(midia, "_nota", None))
                data_conclusao = getattr(midia, "data_conclusao", getattr(midia, "_data_conclusao", None))
                data_conclusao_str = data_conclusao.isoformat() if data_conclusao else None

                tipo_norm = _normalizar_tipo(m_tipo)
                tipo_str = m_tipo.value if hasattr(m_tipo, "value") else str(m_tipo)
                duracao_val = getattr(midia, "duracao_minutos", getattr(midia, "_duracao_minutos", 0)) if tipo_norm == "FILME" else 0

                if m_id is None:
                    cursor.execute(
                        """INSERT INTO midias (titulo, tipo, genero, ano, duracao_minutos, classificacao, status, nota, data_conclusao)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            m_titulo,
                            tipo_str,
                            m_genero,
                            m_ano,
                            duracao_val,
                            m_classificacao,
                            status_str,
                            nota_valor,
                            data_conclusao_str,
                        ),
                    )
                    _definir_id_seguro(midia, cursor.lastrowid)
                else:
                    cursor.execute(
                        """UPDATE midias SET titulo=?, tipo=?, genero=?, ano=?, duracao_minutos=?, classificacao=?, status=?, nota=?, data_conclusao=?
                           WHERE id=?""",
                        (
                            m_titulo,
                            tipo_str,
                            m_genero,
                            m_ano,
                            duracao_val,
                            m_classificacao,
                            status_str,
                            nota_valor,
                            data_conclusao_str,
                            m_id,
                        ),
                    )

                if isinstance(midia, Serie) or tipo_norm == "SERIE":
                    m_id_atual = _obter_id_midia(midia)
                    cursor.execute("DELETE FROM temporadas WHERE serie_id = ?", (m_id_atual,))

                    for temporada in getattr(midia, "temporadas", []):
                        cursor.execute(
                            "INSERT INTO temporadas (serie_id, numero) VALUES (?, ?)",
                            (m_id_atual, temporada.numero),
                        )
                        temporada_id = cursor.lastrowid

                        for ep in temporada.episodios:
                            ep_status = getattr(ep, "status", getattr(ep, "_status", StatusVisualizacao.NAO_ASSISTIDO))
                            ep_status_str = ep_status.value if hasattr(ep_status, "value") else str(ep_status)
                            ep_nota = getattr(ep, "nota", getattr(ep, "_nota", None))
                            ep_titulo = getattr(ep, "titulo", getattr(ep, "_titulo", ""))
                            ep_duracao = getattr(ep, "duracao_minutos", getattr(ep, "_duracao_minutos", 0))

                            cursor.execute(
                                """INSERT INTO episodios (temporada_id, numero_episodio, titulo, duracao_minutos, status, nota)
                                   VALUES (?, ?, ?, ?, ?, ?)""",
                                (
                                    temporada_id,
                                    ep.numero_episodio,
                                    ep_titulo,
                                    ep_duracao,
                                    ep_status_str,
                                    ep_nota,
                                ),
                            )

    def carregar_todos(self) -> list[Midia]:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM midias")
            linhas = cursor.fetchall()

            midias = []
            for linha in linhas:
                try:
                    m = self._converter_linha_para_midia(conexao, linha)
                    if m:
                        midias.append(m)
                except Exception:
                    continue

            return midias

    def listar_todas(self) -> list[Midia]:
        return self.carregar_todos()

    def obter_por_id(self, midia_id: int) -> Midia | None:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM midias WHERE id = ?", (midia_id,))
            linha = cursor.fetchone()
            if linha:
                try:
                    return self._converter_linha_para_midia(conexao, linha)
                except Exception:
                    pass
        return next((m for m in self.carregar_todos() if _obter_id_midia(m) == midia_id), None)

    def adicionar(self, midia: Midia) -> Midia:
        self.salvar_todos([midia])
        return midia

    def atualizar(self, midia: Midia) -> None:
        self.salvar_todos([midia])


class MidiaRepositorySincronizado(MidiaRepository):
    """Repositório híbrido que sincroniza operações de escrita no SQLite e JSON simultaneamente."""

    def __init__(self):
        self.sqlite_repo = MidiaRepositorySQLite()
        self.json_repo = MidiaRepositoryJSON()

    def salvar_todos(self, midias: list[Midia]) -> None:
        self.sqlite_repo.salvar_todos(midias)
        self.json_repo.salvar_todos(midias)

    def carregar_todos(self) -> list[Midia]:
        try:
            midias = self.sqlite_repo.carregar_todos()
            if midias:
                return midias
        except Exception:
            pass
        return self.json_repo.carregar_todos()

    def listar_todas(self) -> list[Midia]:
        return self.carregar_todos()

    def obter_por_id(self, midia_id: int) -> Midia | None:
        m = self.sqlite_repo.obter_por_id(midia_id)
        if m:
            return m
        return self.json_repo.obter_por_id(midia_id)

    def adicionar(self, midia: Midia) -> Midia:
        midia_criada = self.sqlite_repo.adicionar(midia)
        midias_json = self.json_repo.carregar_todos()
        m_id = _obter_id_midia(midia_criada)
        midias_json = [m for m in midias_json if _obter_id_midia(m) != m_id]
        midias_json.append(midia_criada)
        self.json_repo.salvar_todos(midias_json)
        return midia_criada

    def atualizar(self, midia: Midia) -> None:
        self.sqlite_repo.atualizar(midia)
        self.json_repo.atualizar(midia)


def get_midia_repository() -> MidiaRepository:
    """Retorna o repositório ativo com suporte a modo SINCRONIZADO, SQLITE ou JSON."""
    tipo_banco = os.getenv("TIPO_BANCO", "").upper()

    if tipo_banco == "JSON":
        return MidiaRepositoryJSON()
    if tipo_banco == "SQLITE":
        return MidiaRepositorySQLite()

    return MidiaRepositorySincronizado()
