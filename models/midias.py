from abc import ABC, abstractmethod
from typing import List
from datetime import date
from models.enums import StatusVisualizacao, TipoMidia

class Midia(ABC):
    """
    Classe base abstrata para representar uma mídia genérica no catálogo.
    Define os atributos e métodos comuns a Filmes e Séries.
    """
    def __init__(self, titulo: str, tipo: TipoMidia, genero: str, ano: int, classificacao_indicativa: str, elenco: List[str]):
        pass
        
    @property
    def titulo(self) -> str:
        """Propriedade para acessar o título da mídia."""
        pass

    @property
    def nota(self) -> float:
        """Propriedade para acessar a nota da mídia (0 a 10)."""
        pass

    @property
    def status(self) -> StatusVisualizacao:
        """Propriedade para acessar o status de visualização."""
        pass

    def avaliar(self, valor: float) -> None:
        """Adiciona uma nova avaliação à mídia."""
        pass

    def alterar_status(self, novo_status: StatusVisualizacao) -> None:
        """Altera o status de visualização da mídia."""
        pass

    def __str__(self) -> str:
        """Exibição formatada da mídia."""
        pass

    def __repr__(self) -> str:
        """Representação formal da mídia."""
        pass

    def __eq__(self, other: object) -> bool:
        """Compara mídias por título, tipo e ano para impedir duplicidades."""
        pass

    def __lt__(self, other: object) -> bool:
        """Permite ordenar as mídias pela nota média."""
        pass


class Filme(Midia):
    """Classe que representa um Filme, herdando de Midia."""
    def __init__(self, titulo: str, genero: str, ano: int, classificacao_indicativa: str, elenco: List[str], duracao_minutos: int):
        pass

    @property
    def duracao_minutos(self) -> int:
        """Propriedade para acessar a duração do filme em minutos (> 0)."""
        pass


class Episodio:
    """Classe que representa um Episódio individual de uma Temporada."""
    def __init__(self, numero_temporada: int, numero_episodio: int, titulo: str, duracao_minutos: int, data_lancamento: date):
        pass

    @property
    def duracao_minutos(self) -> int:
        """Duração do episódio em minutos (> 0)."""
        pass

    @property
    def status(self) -> StatusVisualizacao:
        """Status de visualização do episódio."""
        pass

    def avaliar(self, valor: float) -> None:
        """Atribui uma nota ao episódio (0 a 10)."""
        pass

    def alterar_status(self, novo_status: StatusVisualizacao) -> None:
        """Altera o status do episódio."""
        pass


class Temporada:
    """Classe que agrega múltiplos episódios de uma Série."""
    def __init__(self, numero: int):
        pass

    def adicionar_episodio(self, episodio: Episodio) -> None:
        """Adiciona um episódio à temporada."""
        pass
        
    def calcular_nota_media(self) -> float:
        """Calcula a nota média baseada nas avaliações dos episódios."""
        pass


class Serie(Midia):
    """Classe que representa uma Série, agregando Temporadas."""
    def __init__(self, titulo: str, genero: str, ano: int, classificacao_indicativa: str, elenco: List[str]):
        pass

    def adicionar_temporada(self, temporada: Temporada) -> None:
        """Adiciona uma nova temporada à série."""
        pass

    def atualizar_status(self) -> None:
        """Marca a série como ASSISTIDA caso todos os episódios estejam concluídos."""
        pass
        
    def __len__(self) -> int:
        """Retorna o número total de episódios na série."""
        pass
