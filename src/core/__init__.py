"""Pacote de configurações e componentes centrais do sistema."""

from .configuracao import Configuracao, configuracao_global
from .events import EventDispatcher

__all__ = [
    "Configuracao",
    "configuracao_global",
    "EventDispatcher"
]
