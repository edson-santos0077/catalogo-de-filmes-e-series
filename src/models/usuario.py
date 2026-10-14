from datetime import datetime, timezone

from models.exceptions import EstadoInvalidoError, ValorInvalidoError
from models.midia import Midia
from models.mixins import SerializavelMixin


class ListaPersonalizada(SerializavelMixin):
    """Classe que agrupa uma coleção de mídias em uma lista temática.

    Attributes:
        nome (str): Nome da lista temática (ex.: 'Favoritos', 'Para Assistir').
        midias (list[Midia]): Lista de mídias agregadas.
    """

    def __init__(self, nome: str):
        super().__init__()
        self.nome = nome
        self._midias: dict[str, Midia] = {}

    @property
    def nome(self) -> str:
        """Retorna o nome da lista personalizada."""
        return self._nome

    @nome.setter
    def nome(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValorInvalidoError(
                "O nome da lista personalizada não pode ser vazio."
            )
        self._nome = valor.strip()

    @property
    def midias(self) -> list[Midia]:
        """Retorna uma lista com todas as mídias cadastradas."""
        return list(self._midias.values())

    def adicionar_midia(self, midia: Midia) -> None:
        """Adiciona uma mídia à lista personalizada utilizando o ID para validação O(1).

        Args:
            midia (Midia): Instância da mídia a ser adicionada.

        Raises:
            TypeError: Se o argumento não for uma instância de Midia.
            ValorInvalidoError: Se a mídia não possuir um ID.
            EstadoInvalidoError: Se a mídia já estiver presente na lista.
        """
        if not isinstance(midia, Midia):
            raise TypeError(
                "O objeto a ser adicionado deve ser uma instância de Midia."
            )
        if not midia.id:
            raise ValorInvalidoError("A mídia deve possuir um ID válido.")

        if midia.id in self._midias:
            raise EstadoInvalidoError(
                f"A mídia '{midia.titulo}' já está presente na lista '{self.nome}'."
            )
        self._midias[midia.id] = midia

    def remover_midia(self, midia: Midia) -> None:
        """Remove uma mídia da lista personalizada.

        Args:
            midia (Midia): Instância da mídia a ser removida.

        Raises:
            TypeError: Se o argumento não for uma instância de Midia.
            EstadoInvalidoError: Se a mídia não for encontrada na lista.
        """
        if not isinstance(midia, Midia):
            raise TypeError("O objeto a ser removido deve ser uma instância de Midia.")

        if midia.id not in self._midias:
            raise EstadoInvalidoError(
                f"A mídia '{midia.titulo}' não se encontra na lista '{self.nome}'."
            )
        del self._midias[midia.id]

    def __len__(self) -> int:
        return len(self._midias)

    def __contains__(self, item: object) -> bool:
        if isinstance(item, Midia) and item.id:
            return item.id in self._midias
        if isinstance(item, str):
            return item in self._midias
        return False

    def __repr__(self) -> str:
        return f"<ListaPersonalizada(nome='{self.nome}', total_midias={len(self)})>"

    def __str__(self) -> str:
        return f"Lista '{self.nome}' ({len(self)} mídia(s))"


class RegistroHistorico(SerializavelMixin):
    """Classe que registra o momento exato da conclusão ou visualização de uma mídia.

    Attributes:
        midia (Midia): Mídia concluída/visualizada.
        data_hora (datetime): Data e hora do registro de conclusão.
    """

    def __init__(self, midia: Midia, data_hora: datetime | None = None):
        super().__init__()
        if not isinstance(midia, Midia):
            raise TypeError("O parâmetro 'midia' deve ser uma instância de Midia.")

        self._midia = midia
        # Corrigido: timezone importado corretamente
        self._data_hora = data_hora or datetime.now(timezone.utc)

    @property
    def midia(self) -> Midia:
        """Retorna a mídia associada ao registro de histórico."""
        return self._midia

    @property
    def data_hora(self) -> datetime:
        """Retorna a data e hora do registro histórico."""
        return self._data_hora

    def __repr__(self) -> str:
        return (
            f"<RegistroHistorico(midia='{self.midia.titulo}', "
            f"data_hora='{self.data_hora.isoformat()}')>"
        )

    def __str__(self) -> str:
        data_formatada = self.data_hora.strftime("%d/%m/%Y %H:%M")
        return f"[{data_formatada}] Concluído: {self.midia.titulo}"


class Usuario(SerializavelMixin):
    """Classe que representa o usuário do sistema e gerencia suas coleções e histórico.

    Attributes:
        id_usuario (str): Identificador único do usuário.
        nome (str): Nome do usuário.
        email (str): Endereço de e-mail do usuário.
        limite_listas (int): Limite máximo de listas personalizadas permitidas.
    """

    def __init__(
        self,
        id_usuario: str,
        nome: str,
        email: str,
        limite_listas: int = 10,
    ):
        super().__init__()
        self.id_usuario = id_usuario
        self.nome = nome
        self.email = email
        self.limite_listas = limite_listas

        self._listas: dict[str, ListaPersonalizada] = {}
        self._favoritos = ListaPersonalizada("Favoritos")
        self._historico: list[RegistroHistorico] = []

    @property
    def id_usuario(self) -> str:
        """Retorna o ID do usuário."""
        return self._id_usuario

    @id_usuario.setter
    def id_usuario(self, valor: str) -> None:
        if not valor or not str(valor).strip():
            raise ValorInvalidoError("O id_usuario não pode ser vazio.")
        self._id_usuario = str(valor).strip()

    @property
    def nome(self) -> str:
        """Retorna o nome do usuário."""
        return self._nome

    @nome.setter
    def nome(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValorInvalidoError("O nome do usuário não pode ser vazio.")
        self._nome = valor.strip()

    @property
    def email(self) -> str:
        """Retorna o e-mail do usuário."""
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        if not valor or "@" not in valor or "." not in valor:
            raise ValorInvalidoError("O e-mail fornecido é inválido.")
        self._email = valor.strip()

    @property
    def limite_listas(self) -> int:
        """Retorna o limite configurado de listas personalizadas."""
        return self._limite_listas

    @limite_listas.setter
    def limite_listas(self, valor: int) -> None:
        if valor <= 0:
            raise ValorInvalidoError("O limite de listas deve ser maior que zero.")
        self._limite_listas = valor

    @property
    def favoritos(self) -> ListaPersonalizada:
        """Retorna a lista de favoritos do usuário."""
        return self._favoritos

    @property
    def historico(self) -> list[RegistroHistorico]:
        """Retorna o histórico de registros de visualizações."""
        return list(self._historico)

    @property
    def listas(self) -> list[ListaPersonalizada]:
        """Retorna todas as listas personalizadas criadas pelo usuário."""
        return list(self._listas.values())

    def criar_lista(self, nome: str) -> ListaPersonalizada:
        """Cria e atribui uma nova lista personalizada ao usuário.

        Args:
            nome (str): Nome da nova lista.

        Returns:
            ListaPersonalizada: A instância da lista criada.

        Raises:
            EstadoInvalidoError: Se o número máximo de listas tiver sido atingido
                ou se já existir uma lista com o mesmo nome.
        """
        if len(self._listas) >= self.limite_listas:
            raise EstadoInvalidoError(
                f"Limite máximo de {self.limite_listas} listas personalizadas atingido."
            )

        nome_normalizado = nome.strip().lower()
        if nome_normalizado in self._listas:
            raise EstadoInvalidoError(f"Já existe uma lista com o nome '{nome}'.")

        nova_lista = ListaPersonalizada(nome)
        self._listas[nome_normalizado] = nova_lista
        return nova_lista

    def obter_lista(self, nome: str) -> ListaPersonalizada:
        """Busca uma lista personalizada criada pelo usuário pelo nome.

        Args:
            nome (str): Nome da lista.

        Returns:
            ListaPersonalizada: Instância da lista solicitada.

        Raises:
            EstadoInvalidoError: Se a lista não for encontrada.
        """
        nome_normalizado = nome.strip().lower()
        if nome_normalizado not in self._listas:
            raise EstadoInvalidoError(f"Lista personalizada '{nome}' não encontrada.")
        return self._listas[nome_normalizado]

    def adicionar_favorito(self, midia: Midia) -> None:
        """Adiciona uma mídia diretamente à lista de favoritos do usuário."""
        self._favoritos.adicionar_midia(midia)

    def remover_favorito(self, midia: Midia) -> None:
        """Remove uma mídia da lista de favoritos do usuário."""
        self._favoritos.remover_midia(midia)

    def registrar_historico(
        self, midia: Midia, data_hora: datetime | None = None
    ) -> RegistroHistorico:
        """Cria e adiciona um novo registro de visualização ao histórico.

        Args:
            midia (Midia): Mídia concluída.
            data_hora (Optional[datetime]): Instância da data/hora de conclusão.

        Returns:
            RegistroHistorico: O registro gerado e encadeado ao histórico.
        """
        registro = RegistroHistorico(midia, data_hora)
        self._historico.append(registro)
        return registro

    def __repr__(self) -> str:
        return f"<Usuario(id='{self.id_usuario}', nome='{self.nome}', email='{self.email}')>"

    def __str__(self) -> str:
        return f"Usuário: {self.nome} ({self.email}) - {len(self._listas)} lista(s)"
