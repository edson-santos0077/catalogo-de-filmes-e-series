import json
import os
from dataclasses import dataclass
from pathlib import Path

# Caminho padrão para o arquivo settings.json dentro de src/core
CAMINHO_SETTINGS_PADRAO = Path(__file__).parent / "settings.json"


@dataclass
class Configuracao:
    """Classe que encapsula os parâmetros de configuração do sistema.

    Attributes:
        nota_minima_recomendado (float): Nota mínima para considerar uma mídia recomendada.
        limite_listas_usuario (int): Limite máximo de listas personalizadas por usuário.
        multiplicador_duracao (float): Multiplicador para conversão de tempo (minutos -> horas).
        casas_decimais_tempo (int): Casas decimais no arredondamento de exibição de tempo.
        backend_persistencia (str): Tipo de repositório padrão ('json' ou 'sqlite').
    """

    nota_minima_recomendado: float = 8.0
    limite_listas_usuario: int = 10
    multiplicador_duracao: float = 1.0
    casas_decimais_tempo: int = 2
    backend_persistencia: str = "json"

    @classmethod
    def carregar(cls, caminho_arquivo: Path | str = CAMINHO_SETTINGS_PADRAO) -> "Configuracao":
        """Carrega e valida as configurações a partir de um arquivo JSON.

        Retorna uma instância de Configuracao com os valores lidos ou com
        os valores padrão caso o arquivo não seja localizado/esteja corrompido.
        """
        caminho = Path(caminho_arquivo)
        if not caminho.exists():
            return cls()

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)

            return cls(
                nota_minima_recomendado=float(dados.get("nota_minima_recomendado", 8.0)),
                limite_listas_usuario=int(dados.get("limite_listas_usuario", 10)),
                multiplicador_duracao=float(dados.get("multiplicador_duracao", 1.0)),
                casas_decimais_tempo=int(dados.get("casas_decimais_tempo", 2)),
                backend_persistencia=str(dados.get("backend_persistencia", "json")).lower(),
            )
        except (json.JSONDecodeError, ValueError, TypeError):
            # Em caso de erro de parse, retorna a configuração padrão segura
            return cls()


# Instância global pronta para ser importada no sistema
configuracao_global = Configuracao.carregar()
