from datetime import datetime

import pytest

# Substitua a linha 4 atual por esta:
from models import Episodio, Filme, Serie, Temporada
from models.enums import StatusVisualizacao, TipoMidia
from models.exceptions import ValorInvalidoError

# --- TESTES DE FILME E VALIDAÇÕES BASE ---


def test_criacao_filme_valido():
    filme = Filme("Inception", "Sci-Fi", 2010, "14", 148, ["Leonardo DiCaprio"])
    assert filme.titulo == "Inception"
    assert filme.tipo == TipoMidia.FILME
    assert filme.duracao_minutos == 148
    assert filme.status == StatusVisualizacao.NAO_ASSISTIDO
    assert filme.data_conclusao is None


def test_validacao_titulo_vazio():
    with pytest.raises(ValorInvalidoError):
        Filme("", "Ação", 2020, "12", 120)


def test_validacao_ano_invalido():
    with pytest.raises(ValorInvalidoError):
        Filme("Filme Antigo", "Drama", -100, "12", 120)


def test_validacao_duracao_filme_invalida():
    with pytest.raises(ValorInvalidoError):
        Filme("Filme Curto", "Ação", 2021, "12", 0)


def test_validacao_nota_fora_do_intervalo():
    filme = Filme("Matrix", "Sci-Fi", 1999, "14", 136)
    with pytest.raises(ValorInvalidoError):
        filme.avaliar(11.0)


def test_validacao_nota_negativa():
    filme = Filme("Matrix", "Sci-Fi", 1999, "14", 136)
    with pytest.raises(ValorInvalidoError):
        filme.avaliar(-1.0)


# --- TESTES DE DATA DE CONCLUSÃO E STATUS ---


def test_atualizacao_automatica_data_conclusao():
    filme = Filme("Interstellar", "Sci-Fi", 2014, "10", 169)
    filme.alterar_status(StatusVisualizacao.ASSISTIDO)

    assert filme.status == StatusVisualizacao.ASSISTIDO
    assert isinstance(filme.data_conclusao, datetime)


def test_remocao_data_conclusao_ao_mudar_status():
    filme = Filme("Interstellar", "Sci-Fi", 2014, "10", 169)
    filme.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme.alterar_status(StatusVisualizacao.NAO_ASSISTIDO)

    assert filme.data_conclusao is None


# --- TESTES DE SÉRIE, TEMPORADA E EPISÓDIO ---


def test_estrutura_serie_temporada_episodio():
    serie = Serie("Breaking Bad", "Drama", 2008, "18")
    temp1 = Temporada(1)
    ep1 = Episodio(1, 1, "Pilot", 58)
    ep2 = Episodio(1, 2, "Cat's in the Bag...", 48)

    temp1.adicionar_episodio(ep1)
    temp1.adicionar_episodio(ep2)
    serie.adicionar_temporada(temp1)

    assert len(serie) == 2  # __len__ calcula o total de episódios
    assert serie.duracao_minutos == 106


def test_adicionar_objeto_invalido_na_temporada():
    temp1 = Temporada(1)

    # O pytest vai esperar que a próxima linha dê um erro do tipo TypeError
    with pytest.raises(TypeError):
        temp1.adicionar_episodio("Isto é uma string, não um episódio")


def test_atualizacao_automatica_status_serie():
    serie = Serie("Dark", "Sci-Fi", 2017, "16")
    temp1 = Temporada(1)
    ep1 = Episodio(1, 1, "Segredos", 51)
    ep2 = Episodio(1, 2, "Lies", 45)

    temp1.adicionar_episodio(ep1)
    temp1.adicionar_episodio(ep2)
    serie.adicionar_temporada(temp1)

    # Inicialmente não assistido
    serie.atualizar_status()
    assert serie.status == StatusVisualizacao.NAO_ASSISTIDO

    # Assistindo 1 episódio -> Série fica ASSISTINDO
    ep1.alterar_status(StatusVisualizacao.ASSISTIDO)
    serie.atualizar_status()
    assert serie.status == StatusVisualizacao.ASSISTINDO

    # Assistindo todos os episódios -> Série fica ASSISTIDA
    ep2.alterar_status(StatusVisualizacao.ASSISTIDO)
    serie.atualizar_status()
    assert serie.status == StatusVisualizacao.ASSISTIDO


def test_calculo_nota_media_serie():
    serie = Serie("Chernobyl", "Drama", 2019, "16")
    temp1 = Temporada(1)
    ep1 = Episodio(1, 1, "1:23:45", 60)
    ep2 = Episodio(1, 2, "Please Remain Calm", 60)

    ep1.avaliar(10.0)
    ep2.avaliar(8.0)

    temp1.adicionar_episodio(ep1)
    temp1.adicionar_episodio(ep2)
    serie.adicionar_temporada(temp1)

    assert serie.nota == 9.0


# --- TESTES DE MÉTODOS ESPECIAIS (__eq__ e __lt__) ---


def test_comparacao_igualdade_midias():
    f1 = Filme("Duna", "Sci-Fi", 2021, "14", 155)
    f2 = Filme("Duna", "Sci-Fi", 2021, "14", 155)
    assert f1 == f2


def test_ordenacao_midias_por_nota():
    f1 = Filme("Filme A", "Ação", 2020, "12", 120)
    f2 = Filme("Filme B", "Ação", 2020, "12", 120)

    f1.avaliar(7.5)
    f2.avaliar(9.0)

    assert f1 < f2
