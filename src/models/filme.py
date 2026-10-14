from models.enums import TipoMidia
from models.exceptions import ValorInvalidoError
from models.midia import Midia


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

    def __init__(
        self,
        titulo: str,
        genero: str,
        ano: int,
        classificacao_indicativa: str,
        duracao_minutos: int,
        elenco: list[str] | None = None,
        id: int | None = None,
    ):
        super().__init__(
            titulo,
            TipoMidia.FILME,
            genero,
            ano,
            classificacao_indicativa,
            elenco,
            id=id,
        )
        self.duracao_minutos = duracao_minutos

    @property
    def duracao_minutos(self) -> int:
        return self._duracao_minutos

    @duracao_minutos.setter
    def duracao_minutos(self, valor: int):
        if valor <= 0:
            raise ValorInvalidoError(
                "A duração do filme deve ser maior que zero minutos."
            )
        self._duracao_minutos = valor

    def __str__(self) -> str:
        return f"Filme: {self.titulo} ({self.ano}) - {self.duracao_minutos} min [{self.status.value}]"
