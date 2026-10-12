import pytest
from models import Filme
from repositories.database import MidiaRepositoryJSON

def test_salvar_e_carregar_filme_json(tmp_path):
    # tmp_path cria uma diretoria temporária única para este teste
    arquivo_temp = tmp_path / "catalogo_teste.json"

    repo = MidiaRepositoryJSON()
    # Sobrescrevemos o caminho padrão para testar de forma isolada
    repo.caminho = str(arquivo_temp)

    filme = Filme("O Padrinho", "Drama", 1972, "16", 175)
    repo.salvar_todos([filme])

    catalogo = repo.carregar_todos()

    assert len(catalogo) == 1
    assert catalogo[0].titulo == "O Padrinho"
    assert isinstance(catalogo[0], Filme)
