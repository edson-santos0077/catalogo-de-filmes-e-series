"""Pacote de modelos do sistema de catálogo de mídias."""
"""Isto permite que as classes, enumerações e exceções sejam importadas
 diretamente a partir do pacote (por exemplo: from models import Filme,
 Serie, Usuario)."""

from .enums import StatusVisualizacao, TipoMidia
from .exceptions import DominioError, EstadoInvalidoError, ValorInvalidoError
from .filme import Filme
from .midia import Midia
from .mixins import AvaliavelMixin, SerializavelMixin
from .serie import Episodio, Serie, Temporada
from .usuario import ListaPersonalizada, RegistroHistorico, Usuario

__all__ = [
    # Enumerações
    "StatusVisualizacao",
    "TipoMidia",
    # Exceções
    "DominioError",
    "EstadoInvalidoError",
    "ValorInvalidoError",
    # Entidades de Mídia
    "Midia",
    "Filme",
    "Serie",
    "Temporada",
    "Episodio",
    # Mixins
    "AvaliavelMixin",
    "SerializavelMixin",
    # Utilizador e Histórico
    "Usuario",
    "ListaPersonalizada",
    "RegistroHistorico",
]
