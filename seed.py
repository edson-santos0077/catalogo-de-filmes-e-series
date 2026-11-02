from src.models.enums import StatusVisualizacao
from src.models.filme import Filme
from src.models.serie import Episodio, Serie, Temporada
from src.models.usuario import Usuario
from src.repositories.midia_repository import get_midia_repository
from src.repositories.usuario_repository import get_usuario_repository


def executar_seed():
    print("Iniciar o povoamento da base de dados...")

    # ==========================================
    # 1. POVOAMENTO DE MÍDIAS
    # ==========================================
    filme1 = Filme(
        titulo="O Senhor dos Anéis: A Sociedade do Anel",
        genero="Fantasia",
        ano=2001,
        duracao_minutos=178,
        classificacao_indicativa="12",
    )
    filme1.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme1.avaliar(10.0)

    filme2 = Filme(
        titulo="Matrix",
        genero="Ficção Científica",
        ano=1999,
        duracao_minutos=136,
        classificacao_indicativa="14",
    )
    filme2.alterar_status(StatusVisualizacao.ASSISTINDO)

    serie1 = Serie(
        titulo="Breaking Bad",
        genero="Drama",
        ano=2008,
        classificacao_indicativa="16",
    )
    temporada1 = Temporada(numero=1)
    ep1 = Episodio(
        numero_temporada=1,
        numero_episodio=1,
        titulo="Pilot",
        duracao_minutos=58,
    )
    ep1.alterar_status(StatusVisualizacao.ASSISTIDO)
    ep1.avaliar(9.5)
    ep2 = Episodio(
        numero_temporada=1,
        numero_episodio=2,
        titulo="Cat's in the Bag...",
        duracao_minutos=48,
    )
    ep2.alterar_status(StatusVisualizacao.ASSISTIDO)
    ep2.avaliar(9.0)
    temporada1.adicionar_episodio(ep1)
    temporada1.adicionar_episodio(ep2)
    serie1.adicionar_temporada(temporada1)
    serie1.atualizar_status()

    filme3 = Filme(
        titulo="O Poderoso Chefão",
        genero="Drama",
        ano=1972,
        duracao_minutos=175,
        classificacao_indicativa="16",
    )
    filme3.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme3.avaliar(9.8)

    filme4 = Filme(
        titulo="Interestelar",
        genero="Ficção Científica",
        ano=2014,
        duracao_minutos=169,
        classificacao_indicativa="10",
    )
    filme4.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme4.avaliar(9.2)

    filme5 = Filme(
        titulo="Pulp Fiction",
        genero="Crime",
        ano=1994,
        duracao_minutos=154,
        classificacao_indicativa="18",
    )
    filme5.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme5.avaliar(9.5)

    filme6 = Filme(
        titulo="O Cavaleiro das Trevas",
        genero="Ação",
        ano=2008,
        duracao_minutos=152,
        classificacao_indicativa="14",
    )
    filme6.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme6.avaliar(9.7)

    filme7 = Filme(
        titulo="Clube da Luta",
        genero="Drama",
        ano=1999,
        duracao_minutos=139,
        classificacao_indicativa="18",
    )
    filme7.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme7.avaliar(8.9)

    filme8 = Filme(
        titulo="A Origem",
        genero="Ficção Científica",
        ano=2010,
        duracao_minutos=148,
        classificacao_indicativa="14",
    )
    filme8.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme8.avaliar(9.1)

    filme9 = Filme(
        titulo="Parasita",
        genero="Suspense",
        ano=2019,
        duracao_minutos=132,
        classificacao_indicativa="16",
    )
    filme9.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme9.avaliar(9.4)

    filme10 = Filme(
        titulo="Whiplash",
        genero="Drama",
        ano=2014,
        duracao_minutos=106,
        classificacao_indicativa="12",
    )
    filme10.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme10.avaliar(8.8)

    filme11 = Filme(
        titulo="A Viagem de Chihiro",
        genero="Animação",
        ano=2001,
        duracao_minutos=125,
        classificacao_indicativa="Livre",
    )
    filme11.alterar_status(StatusVisualizacao.ASSISTIDO)
    filme11.avaliar(9.6)

    serie2 = Serie(
        titulo="Game of Thrones",
        genero="Fantasia",
        ano=2011,
        classificacao_indicativa="18",
    )
    temporada1_got = Temporada(numero=1)
    ep1_got = Episodio(
        numero_temporada=1,
        numero_episodio=1,
        titulo="Winter Is Coming",
        duracao_minutos=62,
    )
    ep1_got.alterar_status(StatusVisualizacao.ASSISTIDO)
    ep1_got.avaliar(8.5)
    temporada1_got.adicionar_episodio(ep1_got)
    serie2.adicionar_temporada(temporada1_got)
    serie2.atualizar_status()

    midias_para_salvar = [
        filme1,
        filme2,
        serie1,
        filme3,
        filme4,
        filme5,
        filme6,
        filme7,
        filme8,
        filme9,
        filme10,
        filme11,
        serie2,
    ]

    repo_midia = get_midia_repository()
    existentes_midias = repo_midia.carregar_todos()

    if len(existentes_midias) == 0:
        repo_midia.salvar_todos(midias_para_salvar)
        print(f"[Mídias] Seed concluído: {len(midias_para_salvar)} mídias inseridas.")
    else:
        print(f"[Mídias] Seed ignorado: A base de dados já contém {len(existentes_midias)} registro(s).")

    # ==========================================
    # 2. POVOAMENTO DE USUÁRIOS
    # ==========================================
    usuario1 = Usuario(
        id_usuario="543604f2-ce60-4b2d-9ea4-632a2ab1368e",
        nome="Edson Santos",
        email="edson@exemplo.com",
    )
    usuario2 = Usuario(
        id_usuario="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        nome="Maria Silva",
        email="maria@exemplo.com",
    )

    usuarios_para_salvar = [usuario1, usuario2]

    repo_usuario = get_usuario_repository()
    existentes_usuarios = repo_usuario.listar_todos()

    if len(existentes_usuarios) == 0:
        for u in usuarios_para_salvar:
            repo_usuario.salvar(u)
        print(f"[Usuários] Seed concluído: {len(usuarios_para_salvar)} usuário(s) inserido(s).")
    else:
        print(f"[Usuários] Seed ignorado: A base de dados já contém {len(existentes_usuarios)} usuário(s).")


if __name__ == "__main__":
    executar_seed()
