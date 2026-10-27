import pytest
import json
from src.models.filme import Filme
from src.models.serie import Serie, Temporada, Episodio
from src.models.usuario import Usuario

# Simulação da classe baseada na sua implementação
class DummyMidiaRepositoryJSON:
    def __init__(self, caminho):
        self.caminho = caminho

    def salvar_todos(self, midias):
        dados = [m.to_dict() for m in midias]
        with open(self.caminho, "w") as f:
            json.dump(dados, f)

    def carregar_todos(self):
        try:
            with open(self.caminho, "r") as f:
                dados = json.load(f)
            # Simplificação para teste. Na real deve checar 'tipo' e usar from_dict
            return [Filme.from_dict(d) if d.get("tipo") == "FILME" else Serie.from_dict(d) for d in dados]
        except FileNotFoundError:
            return []

# --- TESTES DE SERIALIZAÇÃO E PERSISTÊNCIA ---

def test_salvar_e_carregar_filme_json(tmp_path, filme_padrao):
    arquivo_temp = tmp_path / "catalogo.json"
    repo = DummyMidiaRepositoryJSON(arquivo_temp)

    repo.salvar_todos([filme_padrao])
    catalogo = repo.carregar_todos()

    assert len(catalogo) == 1
    assert catalogo[0].titulo == "O Padrinho"
    assert isinstance(catalogo[0], Filme)

def test_salvar_e_carregar_serie_com_episodios(tmp_path, serie_padrao):
    arquivo_temp = tmp_path / "catalogo_series.json"
    repo = DummyMidiaRepositoryJSON(arquivo_temp)

    repo.salvar_todos([serie_padrao])

    # Valida que o JSON guardou toda a árvore de temporadas e episódios
    with open(arquivo_temp, "r") as f:
        dados = json.load(f)
        assert dados[0]["titulo"] == "Breaking Bad"
        assert len(dados[0]["temporadas"]) == 1

def test_carregar_json_inexistente_retorna_lista_vazia(tmp_path):
    arquivo_temp = tmp_path / "nao_existe.json"
    repo = DummyMidiaRepositoryJSON(arquivo_temp)

    assert repo.carregar_todos() == []

def test_sobrescrever_dados_no_json(tmp_path, filme_padrao, serie_padrao):
    arquivo_temp = tmp_path / "catalogo.json"
    repo = DummyMidiaRepositoryJSON(arquivo_temp)

    repo.salvar_todos([filme_padrao])
    assert len(repo.carregar_todos()) == 1

    # Sobrescreve com 2 itens
    repo.salvar_todos([filme_padrao, serie_padrao])
    assert len(repo.carregar_todos()) == 2

def test_mixins_serializavel_enum(filme_padrao):
    # O Filme deve ter o Enum TipoMidia convertido para string "FILME"
    dicionario = filme_padrao.to_dict()
    assert dicionario["tipo"] == "FILME"
    assert "status" in dicionario

def test_mixins_serializavel_data(filme_padrao, data_hoje):
    filme_padrao.data_conclusao = data_hoje
    dicionario = filme_padrao.to_dict()
    assert isinstance(dicionario["data_conclusao"], str) # Data foi convertida para ISO 8601

def test_from_dict_ignora_campos_extras():
    dados_poluidos = {
        "titulo": "Alien", "tipo": "FILME", "genero": "Terror",
        "ano": 1979, "classificacao_indicativa": "16", "duracao_minutos": 117,
        "campo_hacker_inventado": "DROP TABLE"
    }
    # from_dict deve ignorar chaves que não estão na assinatura do __init__
    filme = Filme.from_dict(dados_poluidos)
    assert filme.titulo == "Alien"
    assert not hasattr(filme, "campo_hacker_inventado")

def test_from_dict_lanca_erro_em_dados_invalidos():
    with pytest.raises(TypeError):
        Filme.from_dict(["não é um", "dicionario"])

def test_salvar_multiplos_usuarios_json(tmp_path, usuario_padrao):
    arquivo_temp = tmp_path / "usuarios.json"
    u2 = Usuario("Maria", "maria@mail.com")

    # Simula salvamento de dicionarios de usuarios
    dados = [usuario_padrao.to_dict(), u2.to_dict()]
    with open(arquivo_temp, "w") as f:
        json.dump(dados, f)

    with open(arquivo_temp, "r") as f:
        recuperado = json.load(f)
        assert len(recuperado) == 2
        assert recuperado[1]["email"] == "maria@mail.com"

def test_salvar_colecoes_do_usuario(usuario_padrao):
    # Testa se o histórico do usuário vira listas e dicionarios via SerializavelMixin
    usuario_padrao.criar_lista("Para ver")
    dicionario = usuario_padrao.to_dict()

    assert "listas" in dicionario
    assert isinstance(dicionario["listas"], list)
