import pytest
from datetime import datetime, timezone
from src.models import Filme, Serie, Usuario
from src.models.enums import TipoMidia

@pytest.fixture
def data_hoje():
    return datetime.now(timezone.utc)

@pytest.fixture
def filme_padrao():
    return Filme(
        titulo="Inception",
        genero="Sci-Fi",
        ano=2010,
        classificacao_indicativa="14",
        duracao_minutos=148
    )

@pytest.fixture
def serie_padrao():
    return Serie(
        titulo="Breaking Bad",
        genero="Drama",
        ano=2008,
        classificacao_indicativa="18"
    )

@pytest.fixture
def usuario_padrao():
    return Usuario(
        nome="João",
        email="joao@email.com"
    )
