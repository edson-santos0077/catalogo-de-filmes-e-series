from datetime import datetime

from models.enums import StatusVisualizacao
from models.midia import Midia


class RelatorioService:
    """Serviço responsável por gerar estatísticas e agregações do catálogo."""

    @staticmethod
    def calcular_ocupacao_por_periodo(
        midias: list[Midia], data_inicio: datetime, data_fim: datetime
    ) -> dict:
        """
        Calcula o tempo total assistido num determinado período.

        Args:
            midias (list[Midia]): Lista de mídias do utilizador.
            data_inicio (datetime): Data de início do filtro.
            data_fim (datetime): Data de fim do filtro.

        Returns:
            dict: Relatório com total em minutos e em horas.
        """
        minutos_gastos = 0

        for midia in midias:
            # Filtra apenas o que foi assistido e possui data de conclusão registada
            if midia.status == StatusVisualizacao.ASSISTIDO and midia.data_conclusao:
                # Verifica se a data de conclusão está dentro do intervalo
                if data_inicio <= midia.data_conclusao <= data_fim:
                    minutos_gastos += midia.duracao_minutos

        # Reutilizamos o método estático da classe Midia para converter!
        horas_gastas = Midia.converter_minutos_para_horas(
            minutos_gastos, casas_decimais=1
        )

        return {
            "periodo": f"{data_inicio.date()} até {data_fim.date()}",
            "total_minutos": minutos_gastos,
            "total_horas": horas_gastas,
        }
