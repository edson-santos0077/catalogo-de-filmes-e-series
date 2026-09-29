from typing import List
from datetime import datetime
from models.midia import Midia

class ListaPersonalizada:
    """Classe que agrupa uma coleção de mídias em uma lista temática."""
    def __init__(self, nome: str):
        pass
        
    def adicionar_midia(self, midia: Midia) -> None:
        """Adiciona uma mídia à lista personalizada."""
        pass
        
    def remover_midia(self, midia: Midia) -> None:
        """Remove uma mídia da lista."""
        pass


class RegistroHistorico:
    """Classe que registra o momento exato da conclusão de uma mídia."""
    def __init__(self, midia: Midia, data_hora: datetime):
        pass
        
    @property
    def data_hora(self) -> datetime:
        """Retorna a data e hora do registro."""
        pass


class Usuario:
    """Classe que representa o usuário do sistema."""
    def __init__(self, id_usuario: str, nome: str, email: str):
        pass
        
    def criar_lista(self, nome: str) -> ListaPersonalizada:
        """Cria e retorna uma nova lista personalizada."""
        pass
        
    def adicionar_favorito(self, midia: Midia) -> None:
        """Adiciona uma mídia à lista de favoritos."""
        pass
