"""Módulo de mixins reutilizáveis para o domínio do sistema.

Fornece comportamentos transversais (como avaliação e serialização) que podem
ser incorporados por diferentes classes da hierarquia sem duplicar código.
"""

from models.enums import Enum
from models.exceptions import ValorInvalidoError


class AvaliavelMixin:
    """Mixin que confere a capacidade de receber e gerir avaliações diretas.

    Proporciona atributos e métodos para atribuir e consultar notas de 0.0 a 10.0.
    Pode ser herdado por qualquer entidade do catálogo que permita avaliação individual
    (ex.: Filme, Episodio).

    Attributes:
        _nota (Optional[float]): Armazena a nota numérica da entidade, ou None caso
            ainda não tenha sido avaliada.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._nota: float | None = None

    @property
    def nota(self) -> float | None:
        """Retorna a nota individual atribuída ao objeto."""
        return self._nota

    @nota.setter
    def nota(self, valor: float) -> None:
        if not isinstance(valor, (int, float)) or isinstance(valor, bool):
            raise ValorInvalidoError("A nota deve ser um valor numérico.")
        if not (0 <= valor <= 10):
            raise ValorInvalidoError("A nota deve estar entre 0.0 e 10.0.")
        self._nota = round(float(valor), 1)

    def avaliar(self, valor: float) -> None:
        """Atribui ou atualiza a nota de avaliação da entidade.

        Args:
            valor (float): Nota numérica a atribuir (deve estar entre 0.0 e 10.0).

        Raises:
            ValorInvalidoError: Se o valor fornecido não for do tipo numérico (int/float)
                ou se estiver fora do intervalo permitido [0.0, 10.0].
        """
        self.nota = valor  # Delega para o setter que faz a validação


class SerializavelMixin:
    """Mixin que confere a capacidade de conversão para estruturas dicionário/JSON.

    Inspeciona dinamicamente os atributos da instância e formata os tipos
    complexos (como Enums e datas) para formatos primitivos serializáveis.
    """

    def to_dict(self) -> dict:
        """Converte os atributos internos da instância num dicionário.

        Processa atributos públicos e protegidos (removendo o prefixo '_'),
        convertendo Enums para os seus valores textuais e datas/horas para
        strings no padrão ISO 8601.

        Returns:
            Dict[str, Any]: Dicionário contendo os dados da instância prontos
                para persistência em ficheiro JSON ou resposta de API.
        """
        dados = {}
        for chave, valor in self.__dict__.items():
            nome_campo = chave.lstrip("_")
            if isinstance(valor, Enum):
                dados[nome_campo] = valor.value
            elif hasattr(valor, "isoformat"):
                dados[nome_campo] = valor.isoformat()
            elif isinstance(valor, list):
                dados[nome_campo] = [
                    item.to_dict() if hasattr(item, "to_dict") else item
                    for item in valor
                ]
            elif isinstance(valor, dict):
                dados[nome_campo] = {
                    k: v.to_dict() if hasattr(v, "to_dict") else v
                    for k, v in valor.items()
                }
            else:
                dados[nome_campo] = valor
        return dados

    @classmethod
    def from_dict(cls, dados: dict):
        """Cria uma instância da classe a partir de um dicionário de dados."""
        if not isinstance(dados, dict):
            raise TypeError("Os dados fornecidos devem ser um dicionário.")

        return cls(**dados)
