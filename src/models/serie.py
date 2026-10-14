from datetime import date

from models.enums import StatusVisualizacao, TipoMidia
from models.exceptions import ValorInvalidoError
from models.midia import Midia
from models.mixins import AvaliavelMixin, SerializavelMixin


class Episodio(AvaliavelMixin, SerializavelMixin):
    """Representa um episódio individual pertencente a uma temporada.

    Entidade autônoma agregada por Temporada, responsável por gerenciar
    seus próprios metadados, duração, data de lançamento, avaliações e
    status individual de visualização.

    Attributes:
            numero_temporada (int): Número identificador da temporada (deve ser > 0).
            numero_episodio (int): Número sequencial do episódio (deve ser > 0).
            titulo (str): Nome/título do episódio (não pode ser vazio).
            duracao_minutos (int): Duração do episódio em minutos (deve ser > 0).
            data_lancamento (Optional[date]): Data oficial de exibição ou lançamento.
            status (StatusVisualizacao): Estado de visualização do episódio (leitura).
            nota (Optional[float]): Avaliação individual entre 0.0 e 10.0 (leitura).
    """

    def __init__(
        self,
        numero_temporada: int,
        numero_episodio: int,
        titulo: str,
        duracao_minutos: int,
        data_lancamento: date | str | None = None,
        id: int | None = None,
    ):
        super().__init__()
        self.id = id
        self.numero_temporada = numero_temporada
        self.numero_episodio = numero_episodio
        self.titulo = titulo
        self.duracao_minutos = duracao_minutos
        self.data_lancamento = data_lancamento
        self._status = StatusVisualizacao.NAO_ASSISTIDO

    @property
    def data_lancamento(self) -> date | None:
        return self._data_lancamento

    @data_lancamento.setter
    def data_lancamento(self, valor: date | str | None):
        if valor is None:
            self._data_lancamento = None
        elif isinstance(valor, date):
            self._data_lancamento = valor
        elif isinstance(valor, str):
            try:
                self._data_lancamento = date.fromisoformat(valor)
            except ValueError:
                raise ValueError(
                    "A data de lançamento em texto deve estar no formato YYYY-MM-DD."
                )
        else:
            raise ValorInvalidoError(
                "A data de lançamento deve ser do tipo date, string no formato ISO ou None."
            )

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str):
        if not valor or not valor.strip():
            raise ValorInvalidoError("O título do episódio não pode ser vazio.")
        self._titulo = valor.strip()

    @property
    def numero_temporada(self) -> int:
        return self._numero_temporada

    @numero_temporada.setter
    def numero_temporada(self, valor: int):
        if valor <= 0:
            raise ValueError("O número da temporada deve ser maior que zero.")
        self._numero_temporada = valor

    @property
    def numero_episodio(self) -> int:
        return self._numero_episodio

    @numero_episodio.setter
    def numero_episodio(self, valor: int):
        if valor <= 0:
            raise ValueError("O número do episódio deve ser maior que zero.")
        self._numero_episodio = valor

    @property
    def duracao_minutos(self) -> int:
        return self._duracao_minutos

    @duracao_minutos.setter
    def duracao_minutos(self, valor: int):
        if valor <= 0:
            raise ValueError("A duração do episódio deve ser maior que zero minutos.")
        self._duracao_minutos = valor

    @property
    def status(self) -> StatusVisualizacao:
        return self._status

    def alterar_status(self, novo_status: StatusVisualizacao) -> None:
        self._status = novo_status

    @property
    def id(self) -> int | None:
        return self._id

    @id.setter
    def id(self, valor: int | None):
        if valor is not None and not isinstance(valor, int):
            try:
                valor = int(valor)
            except (ValueError, TypeError):
                raise ValorInvalidoError("O ID deve ser um número inteiro válido.")
        self._id = valor

    def __repr__(self) -> str:
        return f"<Episodio(id='{self.id}', T{self.numero_temporada:02d}E{self.numero_episodio:02d} - '{self.titulo}')>"

    def __str__(self) -> str:
        return f"T{self.numero_temporada:02d}E{self.numero_episodio:02d} - {self.titulo} ({self.duracao_minutos} min) [{self.status.value}]"


class Temporada(SerializavelMixin):
    """Agrega e gerencia os episódios pertencentes a uma temporada.

    Calcula de forma dinâmica a duração total da temporada a partir do somatório
    de seus episódios e computa a média ponderada das avaliações recebidas.

    Attributes:
            numero (int): Número sequencial da temporada (deve ser > 0).
            episodios (List[Episodio]): Lista contendo os episódios agregados.
    """

    def __init__(self, numero: int):
        super().__init__()
        self.numero = numero
        self.episodios: list[Episodio] = []

    @property
    def numero(self) -> int:
        return self._numero

    @numero.setter
    def numero(self, valor: int):
        if valor <= 0:
            raise ValueError("O número da temporada deve ser maior que zero.")
        self._numero = valor

    def adicionar_episodio(self, episodio: Episodio) -> None:
        if not isinstance(episodio, Episodio):
            raise TypeError(
                "O objeto a ser adicionado deve ser uma instância de Episodio."
            )
        self.episodios.append(episodio)

    @property
    def duracao_minutos(self) -> int:
        return sum(ep.duracao_minutos for ep in self.episodios)

    def calcular_nota_media(self) -> float | None:
        avaliados = [ep.nota for ep in self.episodios if ep.nota is not None]
        if not avaliados:
            return None
        return sum(avaliados) / len(avaliados)

    def __len__(self) -> int:
        return len(self.episodios)

    def __repr__(self) -> str:
        return f"<Temporada(numero={self.numero}, total_episodios={len(self)})>"

    def __str__(self) -> str:
        return f"Temporada {self.numero} ({len(self)} episódios)"


class Serie(Midia):
    """Representa uma série de televisão composta por temporadas e episódios.

    Subclasse de Midia que compõe instâncias de Temporada, calculando dinamicamente
    sua duração total, nota média do catálogo e atualizações automáticas de
    status conforme o progresso dos episódios assistidos.

    Attributes:
            titulo (str): Título principal da série.
            genero (str): Gênero principal.
            ano (int): Ano de lançamento ou estreia.
            classificacao_indicativa (str): Faixa etária recomendada.
            elenco (Optional[List[str]]): Lista de atores participantes.
            temporadas (List[Temporada]): Lista de temporadas contidas na série.
    """

    def __init__(
        self,
        titulo: str,
        genero: str,
        ano: int,
        classificacao_indicativa: str,
        elenco: list[str] | None = None,
        id: int | None = None,
    ):
        super().__init__(
            titulo,
            TipoMidia.SERIE,
            genero,
            ano,
            classificacao_indicativa,
            elenco,
            id=id,
        )
        self.temporadas: list[Temporada] = []

    def adicionar_temporada(self, temporada: Temporada) -> None:
        if not isinstance(temporada, Temporada):
            raise TypeError(
                "O objeto a ser adicionado deve ser uma instância de Temporada."
            )
        self.temporadas.append(temporada)

    @property
    def duracao_minutos(self) -> int:
        return sum(temp.duracao_minutos for temp in self.temporadas)

    @property
    def nota(self) -> float | None:
        notas_temporadas = [t.calcular_nota_media() for t in self.temporadas]
        notas_validas = [n for n in notas_temporadas if n is not None]
        if not notas_validas:
            return self._nota
        return sum(notas_validas) / len(notas_validas)

    def atualizar_status(self) -> None:
        todos_episodios = [ep for t in self.temporadas for ep in t.episodios]
        if not todos_episodios:
            return

        # Agora usamos self.alterar_status() para garantir que a data de conclusão
        # seja registada automaticamente pela classe pai (Midia)
        if all(ep.status == StatusVisualizacao.ASSISTIDO for ep in todos_episodios):
            self.alterar_status(StatusVisualizacao.ASSISTIDO)
        elif any(
            ep.status in (StatusVisualizacao.ASSISTIDO, StatusVisualizacao.ASSISTINDO)
            for ep in todos_episodios
        ):
            self.alterar_status(StatusVisualizacao.ASSISTINDO)
        else:
            self.alterar_status(StatusVisualizacao.NAO_ASSISTIDO)

    def __len__(self) -> int:
        return sum(len(t) for t in self.temporadas)

    def __str__(self) -> str:
        return f"Série: {self.titulo} ({self.ano}) - {len(self.temporadas)} temporada(s), {len(self)} episódio(s) [{self.status.value}]"
