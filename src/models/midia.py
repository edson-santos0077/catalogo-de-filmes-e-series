from abc import ABC, abstractmethod
from datetime import date, datetime, timezone

from src.models.enums import StatusVisualizacao, TipoMidia
from src.models.exceptions import EstadoInvalidoError, ValorInvalidoError
from src.models.mixins import AvaliavelMixin, SerializavelMixin


class Midia(AvaliavelMixin, SerializavelMixin, ABC):
    """Representa uma mídia abstrata no catálogo de conteúdos.

    Atua como a classe base abstrata (ABC) para todos os tipos de conteúdos
    audiovisuais (ex.: Filme, Serie), encapsulando atributos comuns como
    metadados, estado de visualização e asvaliações, além de definir a
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

    def __init__(
        self,
        titulo: str,
        tipo: TipoMidia,
        genero: str,
        ano: int,
        classificacao_indicativa: str,
        elenco: list[str] | None = None,
        id: int | None = None,
    ):
        super().__init__()
        self.id = id
        self.titulo = titulo
        self._tipo = tipo
        self.genero = genero
        self.ano = ano
        self.classificacao_indicativa = classificacao_indicativa
        self.elenco = elenco or []
        self._status = StatusVisualizacao.NAO_ASSISTIDO
        self._data_conclusao: datetime | None = None

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str):
        if not valor or not valor.strip():
            raise ValorInvalidoError("O título não pode ser vazio.")
        self._titulo = valor.strip()

    @property
    def genero(self) -> str:
        return self._genero

    @genero.setter
    def genero(self, valor: str):
        if not valor or not valor.strip():
            raise ValorInvalidoError("O gênero não pode ser vazio.")
        self._genero = valor.strip()

    @property
    def ano(self) -> int:
        return self._ano

    @ano.setter
    def ano(self, valor: int):
        if valor <= 0:
            raise ValorInvalidoError("O ano deve ser um valor positivo.")
        self._ano = valor

    @property
    def tipo(self) -> TipoMidia:
        return self._tipo

    @property
    def elenco(self) -> list[str]:
        return self._elenco

    @elenco.setter
    def elenco(self, valor: list[str] | None):
        if valor is None:
            self._elenco = []
        elif isinstance(valor, list):
            if not all(isinstance(item, str) and item.strip() for item in valor):
                raise ValorInvalidoError(
                    "Todos os itens do elenco devem ser strings não vazias."
                )
            self._elenco = [item.strip() for item in valor]
        else:
            raise TypeError("O elenco deve ser uma lista de strings.")

    @property
    def data_conclusao(self) -> datetime | None:
        return self._data_conclusao

    @data_conclusao.setter
    def data_conclusao(self, valor: datetime | date | str | None):
        if valor is None:
            self._data_conclusao = None
        elif isinstance(valor, datetime):
            # Se for datetime naive, adiciona o fuso horário UTC
            if valor.tzinfo is None:
                self._data_conclusao = valor.replace(tzinfo=timezone.utc)
            else:
                self._data_conclusao = valor
        elif isinstance(valor, date):
            # Ao converter de date para datetime, já injeta o timezone UTC
            self._data_conclusao = datetime.combine(
                valor, datetime.min.time(), tzinfo=timezone.utc
            )
        elif isinstance(valor, str):
            try:
                dt_convertido = datetime.fromisoformat(valor)
                # Garante UTC se a string ISO não possuir offset de timezone
                if dt_convertido.tzinfo is None:
                    dt_convertido = dt_convertido.replace(tzinfo=timezone.utc)
                self._data_conclusao = dt_convertido
            except ValueError:
                raise ValorInvalidoError(
                    "A data de conclusão deve estar no formato ISO (ex.: YYYY-MM-DDTHH:MM:SS)."
                )
        else:
            raise TypeError(
                "A data de conclusão deve ser do tipo datetime, date, string no formato ISO ou None."
            )

    @property
    def status(self) -> StatusVisualizacao:
        return self._status

    def alterar_status(self, novo_status: StatusVisualizacao) -> None:
        if not isinstance(novo_status, StatusVisualizacao):
            raise EstadoInvalidoError("O status informado é inválido.")

        self._status = novo_status
        if novo_status == StatusVisualizacao.ASSISTIDO and self._data_conclusao is None:
            self.data_conclusao = datetime.now(timezone.utc)
        elif novo_status != StatusVisualizacao.ASSISTIDO:
            self.data_conclusao = None

        # Disparo do evento do Observer
        EventDispatcher().emitir(
            "STATUS_ALTERADO",
            {
                "id": self.id,
                "titulo": self.titulo,
                "de": status_anterior.value,
                "para": novo_status.value,
            },
        )

    @property
    @abstractmethod
    def duracao_minutos(self) -> int:
        """Retorna a duração total em minutos."""

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

    def __eq__(self, outro: object) -> bool:
        if not isinstance(outro, Midia):
            return False
        if self.id is not None and outro.id is not None:
            return self.id == outro.id
        return (
            self.titulo.lower() == outro.titulo.lower()
            and self._tipo == outro._tipo
            and self.ano == outro.ano
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id='{self.id}', titulo='{self.titulo}', ano={self.ano})>"

    def __lt__(self, outro: object) -> bool:
        if not isinstance(outro, Midia):
            return NotImplemented
        nota_self = self.nota if self.nota is not None else -1.0
        nota_outro = outro.nota if outro.nota is not None else -1.0
        return nota_self < nota_outro

    def __str__(self) -> str:
        return f"{self.titulo} ({self.ano}) - {self.genero} [{self.status.value}]"

    @staticmethod
    def converter_minutos_para_horas(
        minutos: int, multiplicador: float = 1.0, casas_decimais: int = 2
    ) -> float:
        """Converte minutos para horas, com multiplicador e arredondamento configuráveis.

        Args:
            minutos (int): A duração em minutos.
            multiplicador (float, opcional): Fator de multiplicação (ex: 1.5 para velocidade maior).
            casas_decimais (int, opcional): Quantidade de casas para o arredondamento. Padrão é 2.

        Returns:
            float: A duração calculada e arredondada em horas.
        """
        if minutos < 0:
            raise ValorInvalidoError("Os minutos não podem ser negativos.")
        if multiplicador < 0:
            raise ValorInvalidoError("O multiplicador não pode ser negativo.")

        horas_calculadas = (minutos / 60.0) * multiplicador
        return round(horas_calculadas, casas_decimais)
