from datetime import datetime, timezone

from src.models.enums import StatusVisualizacao
from src.models.midia import Midia


class RelatorioService:
    """
    Serviço responsável por gerar estatísticas, relatórios e agregações do catálogo.

    Esta classe concentra as regras de negócio para cálculos de métricas de
    consumo de mídias pelos utilizadores.
    """

    @staticmethod
    def calcular_ocupacao_por_periodo(
        midias: list[Midia], data_inicio: datetime, data_fim: datetime
    ) -> dict:
        """
        Calcula o tempo total gasto a assistir a mídias num determinado período.

        Filtra a lista de mídias para contabilizar apenas aquelas que possuem
        o status de 'ASSISTIDO' e cuja data de conclusão está dentro do intervalo
        fornecido. O resultado é retornado tanto em minutos absolutos como
        convertido para horas, respeitando o arredondamento global configurado.

        Args:
            midias (list[Midia]): Lista de mídias do utilizador a ser analisada.
            data_inicio (datetime): Data de início do intervalo de filtro.
            data_fim (datetime): Data limite do intervalo de filtro.

        Returns:
            dict: Um dicionário contendo as seguintes chaves:
                - 'periodo' (str): Representação em texto do intervalo filtrado.
                - 'total_minutos' (int): A soma de minutos gastos.
                - 'total_horas' (float): O total convertido para horas com base
                  nas configurações dinâmicas do sistema.
        """

        # Garante que as datas de limite possuam timezone (UTC) para evitar TypeError
        if data_inicio.tzinfo is None:
            data_inicio = data_inicio.replace(tzinfo=timezone.utc)
        if data_fim.tzinfo is None:
            data_fim = data_fim.replace(tzinfo=timezone.utc)

        minutos_gastos = 0

        for midia in midias:
            # Filtra apenas o que foi assistido e possui data de conclusão registada
            if midia.status == StatusVisualizacao.ASSISTIDO and midia.data_conclusao:
                # Verifica se a data de conclusão está dentro do intervalo
                if data_inicio <= midia.data_conclusao <= data_fim:
                    minutos_gastos += midia.duracao_minutos

        # Reutiliza o método estático da classe Midia para converter!
        horas_gastas = Midia.converter_minutos_para_horas(
            minutos_gastos, casas_decimais=configuracao_global.casas_decimais_tempo
        )

        return {
            "periodo": f"{data_inicio.date()} até {data_fim.date()}",
            "total_minutos": minutos_gastos,
            "total_horas": horas_gastas,
        }
