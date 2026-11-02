from datetime import datetime, timedelta, timezone
import pytest
from src.services.relatorio import RelatorioService
from src.models.enums import StatusVisualizacao
from src.models.midia import Midia
from src.models.exceptions import ValorInvalidoError

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

def test_top_10_ignora_midia_assistida_sem_nota(filme_padrao):
    from src.models.enums import StatusVisualizacao
    from src.services.relatorio import RelatorioService

    # Filme assistido, mas sem avaliação (nota = 0.0)
    filme_padrao.alterar_status(StatusVisualizacao.ASSISTIDO)

    top_10 = RelatorioService.obter_top_10([filme_padrao])

    # Não deve aparecer no Top 10 pois não possui nota atribuída
    assert len(top_10) == 0
