from src.core.events import Evento, Observer
from src.models.enums import StatusVisualizacao
from src.models.midia import Midia


class Catalogo:
    """Classe agregadora que atua como Sujeito (Subject) no Padrão Observer para gestão de mídias."""

    def __init__(self):
        """
        Inicializa uma nova instância do Catálogo.
        Cria as listas internas vazias para armazenar as mídias e os observadores inscritos.
        """
        self._midias: list[Midia] = []
        self._observadores: list[Observer] = []

    def inscrever(self, observador: Observer) -> None:
        """
        Regista um novo observador para ser notificado sobre eventos do catálogo.

        Args:
            observador (Observer): Instância de uma classe que implementa a interface Observer.
        """
        if observador not in self._observadores:
            self._observadores.append(observador)

    def desinscrever(self, observador: Observer) -> None:
        """
        Remove um observador previamente registado da lista de notificações.

        Args:
            observador (Observer): Instância do observador a ser removido.
        """
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar(self, nome_evento: str, dados: dict) -> None:
        """
        Cria e emite um evento para todos os observadores inscritos.

        Args:
            nome_evento (str): O nome ou identificador do evento ocorrido.
            dados (dict): Dicionário contendo os detalhes e metadados do evento.
        """
        evento = Evento(nome=nome_evento, dados=dados)
        for obs in self._observadores:
            obs.notificar(evento)

    def alterar_status_midia(
        self, midia: Midia, novo_status: StatusVisualizacao
    ) -> None:
        """
        Altera o status de visualização de uma mídia e dispara um evento de notificação.

        Args:
            midia (Midia): A instância da mídia que terá o seu status alterado.
            novo_status (StatusVisualizacao): O novo status a ser atribuído à mídia.
        """
        de_status = midia.status.value
        midia.alterar_status(novo_status)

        self.notificar(
            "STATUS_ALTERADO",
            {"titulo": midia.titulo, "de": de_status, "para": novo_status.value},
        )
