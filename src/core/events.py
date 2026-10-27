from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

@dataclass
class Evento:
    """Representa um evento ocorrido no domínio."""
    nome: str
    dados: dict[str, Any]
    data_hora: datetime = None

    def __post_init__(self):
        if self.data_hora is None:
            self.data_hora = datetime.now(timezone.utc)


class Observer(ABC):
    """Interface abstrata para observadores de eventos."""
    @abstractmethod
    def notificar(self, evento: Evento) -> None:
        pass


class EventDispatcher:
    """Gerenciador centralizado de inscrições e emissão de eventos."""
    _instancia = None
    _observadores: list[Observer] = []

    def __new__(cls):
        # Singleton simples para garantir um barramento único na aplicação
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._observadores = []
        return cls._instancia

    def inscrever(self, observador: Observer) -> None:
        if observador not in self._observadores:
            self._observadores.append(observador)

    def desinscrever(self, observador: Observer) -> None:
        if observador in self._observadores:
            self._observadores.remove(observador)

    def emitir(self, nome_evento: str, dados: dict[str, Any]) -> None:
        evento = Evento(nome=nome_evento, dados=dados)
        for observador in self._observadores:
            observador.notificar(evento)
