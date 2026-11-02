from datetime import datetime, timezone
from typing import List

from src.models.enums import StatusVisualizacao
from src.models.midia import Midia
from src.core.configuracao import configuracao_global


class RelatorioService:
    """
    Serviço responsável por gerar estatísticas, relatórios e agregações do catálogo.

    Esta classe concentra as regras de negócio para cálculos de métricas de
    consumo de mídias pelos utilizadores.
    """

    @staticmethod
    def tempo_total_assistido_por_tipo(midias: List[Midia]) -> dict:
        """
        Calcula o tempo total assistido agrupado por tipo de mídia (Filme/Serie).
        Considera apenas mídias com o status 'ASSISTIDO'.
        """
        # Inicializa os contadores
        minutos_por_tipo = {
            TipoMidia.FILME.value: 0,
            TipoMidia.SERIE.value: 0
        }

        # Soma os minutos
        for midia in midias:
            if midia.status == StatusVisualizacao.ASSISTIDO:
                tipo_str = midia.tipo.value
                minutos_por_tipo[tipo_str] += midia.duracao_minutos

        # Converte para horas usando as configurações globais
        horas_por_tipo = {}
        for tipo, minutos in minutos_por_tipo.items():
            horas_por_tipo[tipo] = Midia.converter_minutos_para_horas(
                minutos, casas_decimais=configuracao_global.casas_decimais_tempo
            )

        return horas_por_tipo


    @staticmethod
    def obter_top_10(midias: List[Midia]) -> List[Midia]:
        """Retorna as 10 mídias assistidas mais bem avaliadas.

        Considera apenas mídias concluídas e com nota atribuída (> 0).
        """
        # 1. Filtra apenas mídias assistidas E que foram avaliadas (nota > 0 e não None)
        avaliadas = [
            m for m in midias
            if m.status == StatusVisualizacao.ASSISTIDO
            and m.nota is not None
            and m.nota > 0
        ]

        # 2. Ordena da maior para a menor nota
        avaliadas_ordenadas = sorted(avaliadas, key=lambda m: m.nota, reverse=True)

        # 3. Retorna os 10 primeiros resultados
        return avaliadas_ordenadas[:10]

    @staticmethod
    def media_notas_por_genero(midias: List[Midia]) -> dict:
        """
        Calcula a média de notas das mídias agrupadas por gênero.

        Considera apenas mídias concluídas (ASSISTIDO) e que foram avaliadas.

        Args:
            midias (List[Midia]): Lista de mídias a ser analisada.

        Returns:
            dict: Dicionário contendo o nome do gênero como chave e a média
                  como valor (ex: {'Drama': 9.2, 'Sci-Fi': 8.5}).
        """
        soma_notas = {}
        contagem_midias = {}

        for m in midias:
            # Regra de negócio: apenas mídias assistidas e com nota válida
            if m.status == StatusVisualizacao.ASSISTIDO and m.nota is not None and m.nota > 0:
                # Padronizar o nome do gênero (capitalizado, ex: "sci-fi" -> "Sci-Fi")
                genero = m.genero.strip().title()

                if genero not in soma_notas:
                    soma_notas[genero] = 0.0
                    contagem_midias[genero] = 0

                soma_notas[genero] += m.nota
                contagem_midias[genero] += 1

        # Calcula a média arredondada para 2 casas decimais
        medias = {}
        for genero in soma_notas:
            media = soma_notas[genero] / contagem_midias[genero]
            medias[genero] = round(media, 2)

        return medias
