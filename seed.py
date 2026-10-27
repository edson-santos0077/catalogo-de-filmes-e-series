from datetime import datetime, timezone
from src.models.enums import TipoMidia, StatusVisualizacao
from src.models.filme import Filme
from src.models.serie import Serie
from src.models.usuario import Usuario
# Ajuste a importação abaixo de acordo com o nome exato da sua classe/ficheiro de repositório
from src.repositories.database import MidiaRepositorySQLite

def executar_seed():
    print("A iniciar o povoamento da base de dados...")

    # 1. Criação de Filmes
    filme1 = Filme(
        titulo="O Senhor dos Anéis: A Sociedade do Anel",
        genero="Fantasia",
        ano=2001,
        duracao_minutos=178,
        classificacao_indicativa=12
    )
    filme1.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme1.nota = 10.0

    filme2 = Filme(
        titulo="Matrix",
        genero="Ficção Científica",
        ano=1999,
        duracao_minutos=136,
        classificacao_indicativa=14
    )
    filme2.alterar_status(StatusVisualizacao.ASSISTINDO)

    # 2. Criação de Séries com Temporadas e Episódios
    serie1 = Serie(
        titulo="Breaking Bad",
        genero="Drama",
        ano=2008,
        classificacao_indicativa=16
    )

    # Adicionando uma temporada e episódios (ajuste os argumentos conforme o seu __init__)
    temporada1 = serie1.adicionar_temporada(numero=1)
    ep1 = temporada1.adicionar_episodio(titulo="Pilot", duracao_minutos=58)
    ep2 = temporada1.adicionar_episodio(titulo="Cat's in the Bag...", duracao_minutos=48)

    # Simulando visualização para engatilhar as regras de negócio
    ep1.alterar_status(StatusVisualizacao.ASSISTIDO)
    ep1.nota = 9.5
    ep2.alterar_status(StatusVisualizacao.ASSISTIDO)
    ep2.nota = 9.0
    # A série deve ser marcada como ASSISTIDA automaticamente através dos métodos internos
    serie1.atualizar_status()

    # 3. Persistência
    repositorio = MidiaRepositorySQLite()
    # O UML indica o método salvar_todos
    midias_para_salvar = [filme1, filme2, serie1]

    try:
        repositorio.salvar_todos(midias_para_salvar)
        print("Povoamento concluído com sucesso! Foram inseridos filmes e séries de teste.")
    except Exception as e:
        print(f"Erro ao guardar na base de dados: {e}")

if __name__ == "__main__":
    executar_seed()
