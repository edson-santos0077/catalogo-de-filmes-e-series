from datetime import datetime, timedelta, timezone
import pytest
from src.services.relatorio import RelatorioService
from src.models.enums import StatusVisualizacao
from src.models.midia import Midia
from src.models.exceptions import ValorInvalidoError

# --- TESTES DE OCUPAÇÃO POR PERÍODO ---

def test_ocupacao_lista_vazia(data_hoje):
    resultado = RelatorioService.calcular_ocupacao_por_periodo([], data_hoje - timedelta(days=1), data_hoje)
    assert resultado["total_minutos"] == 0
    assert resultado["total_horas"] == 0.0

def test_ocupacao_ignora_midias_nao_assistidas(filme_padrao, data_hoje):
    filme_padrao.alterar_status(StatusVisualizacao.NAO_ASSISTIDO)
    resultado = RelatorioService.calcular_ocupacao_por_periodo([filme_padrao], data_hoje - timedelta(days=10), data_hoje)
    assert resultado["total_minutos"] == 0

def test_ocupacao_soma_apenas_dentro_do_periodo(filme_padrao, serie_padrao, data_hoje):
    filme_padrao.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme_padrao.data_conclusao = data_hoje - timedelta(days=5) # Dentro do período

    serie_padrao.atualizar_status() # Não assistido

    resultado = RelatorioService.calcular_ocupacao_por_periodo(
        [filme_padrao, serie_padrao],
        data_hoje - timedelta(days=10),
        data_hoje
    )
    assert resultado["total_minutos"] == 175 # Apenas a duração do filme

def test_ocupacao_ignora_midias_fora_do_periodo(filme_padrao, data_hoje):
    filme_padrao.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme_padrao.data_conclusao = data_hoje - timedelta(days=20) # Fora

    resultado = RelatorioService.calcular_ocupacao_por_periodo([filme_padrao], data_hoje - timedelta(days=10), data_hoje)
    assert resultado["total_minutos"] == 0

def test_ocupacao_datas_limites_inclusivas(filme_padrao, data_hoje):
    filme_padrao.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme_padrao.data_conclusao = data_hoje # Exatamente no limite

    resultado = RelatorioService.calcular_ocupacao_por_periodo([filme_padrao], data_hoje - timedelta(days=1), data_hoje)
    assert resultado["total_minutos"] == 175

def test_ocupacao_suporta_datas_sem_timezone(filme_padrao):
    filme_padrao.alterar_status(StatusVisualizacao.ASSISTIDO)
    dt_inicio_naive = datetime(2023, 1, 1)
    dt_fim_naive = datetime(2023, 12, 31)
    filme_padrao.data_conclusao = datetime(2023, 6, 15, tzinfo=timezone.utc)

    # Não deve lançar TypeError
    resultado = RelatorioService.calcular_ocupacao_por_periodo([filme_padrao], dt_inicio_naive, dt_fim_naive)
    assert resultado["total_minutos"] == 175

# --- TESTES DE CONVERSÃO DE TEMPO (MÉTODO ESTÁTICO) ---

def test_conversao_minutos_para_horas_padrao():
    assert Midia.converter_minutos_para_horas(120) == 2.0
    assert Midia.converter_minutos_para_horas(90) == 1.5

def test_conversao_minutos_para_horas_com_arredondamento():
    assert Midia.converter_minutos_para_horas(100, casas_decimais=1) == 1.7 # 1.666...
    assert Midia.converter_minutos_para_horas(100, casas_decimais=3) == 1.667

def test_conversao_minutos_com_multiplicador_de_velocidade():
    # Assistindo 120 minutos em velocidade 1.5x demora 80 minutos reais (1.33 horas)
    assert Midia.converter_minutos_para_horas(120, multiplicador=0.5) == 1.0

def test_conversao_rejeita_minutos_negativos():
    with pytest.raises(ValorInvalidoError):
        Midia.converter_minutos_para_horas(-10)

def test_conversao_rejeita_multiplicador_negativo():
    with pytest.raises(ValorInvalidoError):
        Midia.converter_minutos_para_horas(100, multiplicador=-1.0)
