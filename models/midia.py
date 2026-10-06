from abc import ABC, abstractmethod
from typing import List, Optional, Union
from datetime import date
from models.enums import StatusVisualizacao, TipoMidia


class Midia(ABC):
    """Representa uma mídia abstrata no catálogo de conteúdos.

    Atua como a classe base abstrata (ABC) para todos os tipos de conteúdos
    audiovisuais (ex.: Filme, Serie), encapsulando atributos comuns como
    metadados, estado de visualização e avaliações, além de definir a
    interface obrigatória para cálculo de duração.

    Attributes:
        titulo (str): Título da mídia (não pode ser vazio).
        tipo (TipoMidia): Tipo da mídia (FILME ou SERIE).
        genero (str): Gênero cinematográfico ou televisivo (não pode ser vazio).
        ano (int): Ano de lançamento da mídia (deve ser um valor positivo).
        classificacao_indicativa (str): Faixa etária recomendada.
        elenco (List[str]): Lista com os nomes do elenco principal.
        status (StatusVisualizacao): Estado atual de consumo (leitura).
        nota (Optional[float]): Nota de avaliação entre 0.0 e 10.0 (leitura).
    """

    def __init__(self, titulo: str, tipo: TipoMidia, genero: str, ano: int, 
                 classificacao_indicativa: str, elenco: Optional[List[str]] = None):
        self.titulo = titulo
        self._tipo = tipo
        self.genero = genero
        self.ano = ano
        self.classificacao_indicativa = classificacao_indicativa
        self.elenco = elenco or []
        self._status = StatusVisualizacao.NAO_ASSISTIDO
        self._nota: Optional[float] = None

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str):
        if not valor or not valor.strip():
            raise ValueError("O título não pode ser vazio.")
        self._titulo = valor.strip()

    @property
    def genero(self) -> str:
        return self._genero

    @genero.setter
    def genero(self, valor: str):
        if not valor or not valor.strip():
            raise ValueError("O gênero não pode ser vazio.")
        self._genero = valor.strip()

    @property
    def ano(self) -> int:
        return self._ano

    @ano.setter
    def ano(self, valor: int):
        if valor <= 0:
            raise ValueError("O ano deve ser um valor positivo.")
        self._ano = valor

    @property
    def tipo(self) -> TipoMidia:
        return self._tipo

    @property
    def nota(self) -> Optional[float]:
        return self._nota

    @property
    def status(self) -> StatusVisualizacao:
        return self._status

    def avaliar(self, valor: float) -> None:
        if not (0 <= valor <= 10):
            raise ValueError("A nota deve estar entre 0 e 10.")
        self._nota = float(valor)

    def alterar_status(self, novo_status: StatusVisualizacao) -> None:
        self._status = novo_status

    @property
    @abstractmethod
    def duracao_minutos(self) -> int:
        """Retorna a duração total em minutos."""
        pass

    def __eq__(self, outro: object) -> bool:
        if not isinstance(outro, Midia):
            return False
        return (
            self.titulo.lower() == outro.titulo.lower() and 
            self._tipo == outro._tipo and 
            self.ano == outro.ano
        )

    def __lt__(self, outro: object) -> bool:
        if not isinstance(outro, Midia):
            return NotImplemented
        nota_self = self.nota if self.nota is not None else -1.0
        nota_outro = outro.nota if outro.nota is not None else -1.0
        return nota_self < nota_outro

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(titulo='{self.titulo}', ano={self.ano})>"

    def __str__(self) -> str:
        return f"{self.titulo} ({self.ano}) - {self.genero} [{self.status.value}]"


class Filme(Midia):
    """Representa um filme individual no catálogo.

    Subclasse de Midia que armazena uma duração fixa em minutos e implementa
    a exibição formatada específica para filmes.

    Attributes:
        titulo (str): Título do filme.
        genero (str): Gênero do filme.
        ano (int): Ano de lançamento.
        classificacao_indicativa (str): Faixa etária recomendada.
        duracao_minutos (int): Duração fixa em minutos (deve ser maior que zero).
        elenco (Optional[List[str]]): Lista de atores participantes.
    """

    def __init__(self, titulo: str, genero: str, ano: int, 
                 classificacao_indicativa: str, duracao_minutos: int, 
                 elenco: Optional[List[str]] = None):
        super().__init__(titulo, TipoMidia.FILME, genero, ano, classificacao_indicativa, elenco)
        self.duracao_minutos = duracao_minutos

    @property
    def duracao_minutos(self) -> int:
        return self._duracao_minutos

    @duracao_minutos.setter
    def duracao_minutos(self, valor: int):
        if valor <= 0:
            raise ValueError("A duração do filme deve ser maior que zero minutos.")
        self._duracao_minutos = valor

    def __str__(self) -> str:
        return f"Filme: {self.titulo} ({self.ano}) - {self.duracao_minutos} min [{self.status.value}]"


class Episodio:
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

    def __init__(self, numero_temporada: int, numero_episodio: int, titulo: str, 
                 duracao_minutos: int, data_lancamento: Optional[Union[date, str]] = None):
        self.numero_temporada = numero_temporada
        self.numero_episodio = numero_episodio
        self.titulo = titulo
        self.duracao_minutos = duracao_minutos
        self.data_lancamento = data_lancamento
        self._status = StatusVisualizacao.NAO_ASSISTIDO
        self._nota: Optional[float] = None

    @property
    def data_lancamento(self) -> Optional[date]:
        return self._data_lancamento

    @data_lancamento.setter
    def data_lancamento(self, valor: Optional[Union[date, str]]):
        if valor is None:
            self._data_lancamento = None
        elif isinstance(valor, date):
            self._data_lancamento = valor
        elif isinstance(valor, str):
            try:
                self._data_lancamento = date.fromisoformat(valor)
            except ValueError:
                raise ValueError("A data de lançamento em texto deve estar no formato YYYY-MM-DD.")
        else:
            raise TypeError("A data de lançamento deve ser do tipo date, string no formato ISO ou None.")

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str):
        if not valor or not valor.strip():
            raise ValueError("O título do episódio não pode ser vazio.")
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

    @property
    def nota(self) -> Optional[float]:
        return self._nota

    def avaliar(self, valor: float) -> None:
        if not (0 <= valor <= 10):
            raise ValueError("A nota do episódio deve estar entre 0 e 10.")
        self._nota = float(valor)

    def alterar_status(self, novo_status: StatusVisualizacao) -> None:
        self._status = novo_status

    def __repr__(self) -> str:
        return f"<Episodio(T{self.numero_temporada:02d}E{self.numero_episodio:02d} - '{self.titulo}')>"

    def __str__(self) -> str:
        return f"T{self.numero_temporada:02d}E{self.numero_episodio:02d} - {self.titulo} ({self.duracao_minutos} min) [{self.status.value}]"


class Temporada:
    """Agrega e gerencia os episódios pertencentes a uma temporada.

    Calcula de forma dinâmica a duração total da temporada a partir do somatório
    de seus episódios e computa a média ponderada das avaliações recebidas.

    Attributes:
        numero (int): Número sequencial da temporada (deve ser > 0).
        episodios (List[Episodio]): Lista contendo os episódios agregados.
    """

    def __init__(self, numero: int):
        self.numero = numero
        self.episodios: List[Episodio] = []

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
            raise TypeError("O objeto a ser adicionado deve ser uma instância de Episodio.")
        self.episodios.append(episodio)

    @property
    def duracao_minutos(self) -> int:
        return sum(ep.duracao_minutos for ep in self.episodios)

    def calcular_nota_media(self) -> Optional[float]:
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

    def __init__(self, titulo: str, genero: str, ano: int, 
                 classificacao_indicativa: str, elenco: Optional[List[str]] = None):
        super().__init__(titulo, TipoMidia.SERIE, genero, ano, classificacao_indicativa, elenco)
        self.temporadas: List[Temporada] = []

    def adicionar_temporada(self, temporada: Temporada) -> None:
        if not isinstance(temporada, Temporada):
            raise TypeError("O objeto a ser adicionado deve ser uma instância de Temporada.")
        self.temporadas.append(temporada)

    @property
    def duracao_minutos(self) -> int:
        return sum(temp.duracao_minutos for temp in self.temporadas)

    @property
    def nota(self) -> Optional[float]:
        notas_temporadas = [t.calcular_nota_media() for t in self.temporadas]
        notas_validas = [n for n in notas_temporadas if n is not None]
        if not notas_validas:
            return self._nota
        return sum(notas_validas) / len(notas_validas)

    def atualizar_status(self) -> None:
        todos_episodios = [ep for t in self.temporadas for ep in t.episodios]
        if not todos_episodios:
            return

        if all(ep.status == StatusVisualizacao.ASSISTIDO for ep in todos_episodios):
            self._status = StatusVisualizacao.ASSISTIDO
        elif any(ep.status in (StatusVisualizacao.ASSISTIDO, StatusVisualizacao.ASSISTINDO) for ep in todos_episodios):
            self._status = StatusVisualizacao.ASSISTINDO
        else:
            self._status = StatusVisualizacao.NAO_ASSISTIDO

    def __len__(self) -> int:
        return sum(len(t) for t in self.temporadas)

    def __str__(self) -> str:
        return f"Série: {self.titulo} ({self.ano}) - {len(self.temporadas)} temporada(s), {len(self)} episódio(s) [{self.status.value}]"
