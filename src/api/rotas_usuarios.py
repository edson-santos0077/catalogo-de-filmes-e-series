import uuid
from typing import List

from fastapi import APIRouter, HTTPException, status

from src.api.schemas import UsuarioCreate, UsuarioResponse, ListaCreate, FavoritoCreate
from src.models.usuario import Usuario
from src.repositories.database import get_usuario_repository
from src.models.exceptions import ValorInvalidoError, EstadoInvalidoError
from src.repositories.database import get_usuario_repository, get_midia_repository




router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario_in: UsuarioCreate):
    repo = get_usuario_repository()

    # Validação de duplicidade delegada ao repositório
    if repo.obter_por_email(usuario_in.email):
        raise HTTPException(status_code=400, detail="E-mail já está em uso.")

    try:
        novo_usuario = Usuario(
            id_usuario=str(uuid.uuid4()),
            nome=usuario_in.nome,
            email=usuario_in.email
        )

        # O repositório real lida com a persistência no banco de dados (SQLite/JSON)
        usuario_salvo = repo.adicionar(novo_usuario)
        return usuario_salvo

    except (ValorInvalidoError, EstadoInvalidoError) as e:
        # Captura regras de domínio quebradas na instanciação (ex: e-mail inválido)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Captura erros inesperados de persistência
        raise HTTPException(status_code=500, detail=f"Erro interno ao criar utilizador: {str(e)}")

@router.get("/{id_usuario}", response_model=UsuarioResponse)
def obter_usuario(id_usuario: str):
    repo = get_usuario_repository()
    usuario = repo.obter_por_id(id_usuario)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return usuario

@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios():
    repo = get_usuario_repository()
    return repo.listar_todos()


# 7. Criar Lista Personalizada (Nova)
@router.post("/{id_usuario}/listas", status_code=status.HTTP_201_CREATED)
def criar_lista(id_usuario: str, lista_in: ListaCreate):
    repo_user = get_usuario_repository()
    usuario = repo_user.obter_por_id(id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    try:
        nova_lista = usuario.criar_lista(lista_in.nome)
        repo_user.atualizar(usuario)
        return {"mensagem": f"Lista '{nova_lista.nome}' criada com sucesso."}
    except (ValorInvalidoError, EstadoInvalidoError) as e:
        raise HTTPException(status_code=400, detail=str(e))

# 8. Adicionar aos Favoritos (Nova)
@router.post("/{id_usuario}/favoritos", status_code=status.HTTP_200_OK)
def adicionar_favorito(id_usuario: str, favorito_in: FavoritoCreate):
    repo_user = get_usuario_repository()
    repo_midia = get_midia_repository()

    usuario = repo_user.obter_por_id(id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    midia = repo_midia.obter_por_id(favorito_in.midia_id)
    if not midia:
        raise HTTPException(status_code=404, detail="Mídia não encontrada.")

    try:
        usuario.adicionar_favorito(midia)
        repo_user.atualizar(usuario)
        return {"mensagem": f"'{midia.titulo}' adicionado aos favoritos."}
    except (ValorInvalidoError, EstadoInvalidoError) as e:
        raise HTTPException(status_code=400, detail=str(e))
