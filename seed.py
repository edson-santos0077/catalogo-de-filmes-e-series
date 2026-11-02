from datetime import datetime, timezone
from src.models.enums import TipoMidia, StatusVisualizacao
from src.models.filme import Filme
from src.models.serie import Serie, Temporada, Episodio
from src.models.usuario import Usuario
# Ajuste a importação abaixo de acordo com o nome exato da sua classe/ficheiro de repositório
from src.repositories.midia_repository import MidiaRepositorySQLite, MidiaRepositoryJSON

def executar_seed():
    print("Iniciar o povoamento da base de dados...")

    # 1. Criação dos objetos de Seed originais
    filme1 = Filme(titulo="O Senhor dos Anéis: A Sociedade do Anel", genero="Fantasia", ano=2001, duracao_minutos=178, classificacao_indicativa="12")
    filme1.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme1.avaliar(10.0)

    filme2 = Filme(titulo="Matrix", genero="Ficção Científica", ano=1999, duracao_minutos=136, classificacao_indicativa="14")
    filme2.alterar_status(StatusVisualizacao.ASSISTINDO) # Não aparecerá no Top 10 (não assistido)

    serie1 = Serie(titulo="Breaking Bad", genero="Drama", ano=2008, classificacao_indicativa="16")
    temporada1 = Temporada(numero=1)
    ep1 = Episodio(numero_temporada=1, numero_episodio=1, titulo="Pilot", duracao_minutos=58)
    ep1.alterar_status(StatusVisualizacao.ASSISTIDO)
    ep1.avaliar(9.5)
    ep2 = Episodio(numero_temporada=1, numero_episodio=2, titulo="Cat's in the Bag...", duracao_minutos=48)
    ep2.alterar_status(StatusVisualizacao.ASSISTIDO)
    ep2.avaliar(9.0)
    temporada1.adicionar_episodio(ep1)
    temporada1.adicionar_episodio(ep2)
    serie1.adicionar_temporada(temporada1)
    serie1.atualizar_status() # Ficou assistida, nota média 9.25

    # 2. Novas Mídias para o Top 10 e Média por Género
    filme3 = Filme(titulo="O Poderoso Chefão", genero="Drama", ano=1972, duracao_minutos=175, classificacao_indicativa="16")
    filme3.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme3.avaliar(9.8)

    filme4 = Filme(titulo="Interestelar", genero="Ficção Científica", ano=2014, duracao_minutos=169, classificacao_indicativa="10")
    filme4.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme4.avaliar(9.2)

    filme5 = Filme(titulo="Pulp Fiction", genero="Crime", ano=1994, duracao_minutos=154, classificacao_indicativa="18")
    filme5.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme5.avaliar(9.5)

    filme6 = Filme(titulo="O Cavaleiro das Trevas", genero="Ação", ano=2008, duracao_minutos=152, classificacao_indicativa="14")
    filme6.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme6.avaliar(9.7)

    filme7 = Filme(titulo="Clube da Luta", genero="Drama", ano=1999, duracao_minutos=139, classificacao_indicativa="18")
    filme7.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme7.avaliar(8.9)

    filme8 = Filme(titulo="A Origem", genero="Ficção Científica", ano=2010, duracao_minutos=148, classificacao_indicativa="14")
    filme8.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme8.avaliar(9.1)

    filme9 = Filme(titulo="Parasita", genero="Suspense", ano=2019, duracao_minutos=132, classificacao_indicativa="16")
    filme9.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme9.avaliar(9.4)

    filme10 = Filme(titulo="Whiplash", genero="Drama", ano=2014, duracao_minutos=106, classificacao_indicativa="12")
    filme10.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme10.avaliar(8.8)

    filme11 = Filme(titulo="A Viagem de Chihiro", genero="Animação", ano=2001, duracao_minutos=125, classificacao_indicativa="Livre")
    filme11.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme11.avaliar(9.6)

    # Série 2
    serie2 = Serie(titulo="Game of Thrones", genero="Fantasia", ano=2011, classificacao_indicativa="18")
    temporada1_got = Temporada(numero=1)
    ep1_got = Episodio(numero_temporada=1, numero_episodio=1, titulo="Winter Is Coming", duracao_minutos=62)
    ep1_got.alterar_status(StatusVisualizacao.ASSISTIDO)
    ep1_got.avaliar(8.5)
    temporada1_got.adicionar_episodio(ep1_got)
    serie2.adicionar_temporada(temporada1_got)
    serie2.atualizar_status() # Assistida, nota 8.5

    # Consolidar a lista
    midias_para_salvar = [
        filme1, filme2, serie1, filme3, filme4, filme5,
        filme6, filme7, filme8, filme9, filme10, filme11, serie2
    ]

    # 2. Configuração dos repositórios
    # Se o MidiaRepositoryJSON precisar de um caminho de arquivos no construtor, passe-o aqui.
    # Exemplo: MidiaRepositoryJSON(os.path.join("data", "midias.json"))
    repositorios = {
        "SQLite": MidiaRepositorySQLite(),
        "JSON": MidiaRepositoryJSON()
    }

    # 3. Execução condicional do Seed
    for nome, repo in repositorios.items():
        try:
            dados_existentes = repo.carregar_todos()

            # Verifica se já existem registos. Se sim, ignora a inserção.
            if len(dados_existentes) > 0:
                print(f"[{nome}] Povoamento ignorado: A base de dados já contém {len(dados_existentes)} registo(s).")
                continue

            # Se estiver vazio, guarda os dados de teste
            repo.salvar_todos(midias_para_salvar)
            print(f"[{nome}] Povoamento concluído com sucesso! {len(midias_para_salvar)} registos inseridos.")

        except Exception as e:
            print(f"[{nome}] Erro ao aceder ou guardar na base de dados: {e}")

if __name__ == "__main__":
    executar_seed()
