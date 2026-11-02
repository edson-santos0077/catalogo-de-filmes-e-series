from typing import List, Dict
from fastapi import APIRouter, HTTPException, status

from src.api.schemas import (
    MidiaCreate, MidiaResponse, AvaliacaoCreate, EpisodioCreate, StatusUpdate
)
from src.models.filme import Filme
from src.models.serie import Serie, Temporada, Episodio
from src.models.enums import TipoMidia
from src.models.exceptions import ValorInvalidoError, EstadoInvalidoError
from src.repositories.midia_repository import get_midia_repository
from src.services.relatorio import RelatorioService
from src.repositories.midia_repository import MidiaRepositorySQLite

router = APIRouter(prefix="/midias", tags=["Mídias"])

# 1. Adicionar Mídia
@router.post("/", status_code=201)
def criar_midia(midia_in: MidiaCreate): # O nome do seu schema Pydantic pode variar
    repo = get_midia_repository()

    # Extrai o tipo de forma segura (lidando com strings ou Enums)
    tipo_str = midia_in.tipo.value if hasattr(midia_in.tipo, 'value') else str(midia_in.tipo)
    tipo_norm = tipo_str.upper()

    # Instancia a classe correta com base no payload
    if "SERI" in tipo_norm or "SÉR" in tipo_norm:
        nova_midia = Serie(
            titulo=midia_in.titulo,
            genero=midia_in.genero,
            ano=midia_in.ano,
            classificacao_indicativa=midia_in.classificacao_indicativa
        )
    else:
        nova_midia = Filme(
            titulo=midia_in.titulo,
            genero=midia_in.genero,
            ano=midia_in.ano,
            duracao_minutos=getattr(midia_in, 'duracao_minutos', 0),
            classificacao_indicativa=midia_in.classificacao_indicativa
        )

    repo.adicionar(nova_midia)
    return nova_midia

# 2. Relatório Top 10 (Deve vir antes do GET /{midia_id})
@router.get("/relatorios/top10", response_model=List[MidiaResponse])
def obter_top_10_midias():
    repo = get_midia_repository()
    todas_midias = repo.carregar_todos()
    return RelatorioService.obter_top_10(todas_midias)

# 3. Listar Mídias
@router.get("/", response_model=List[MidiaResponse])
def listar_midias():
    repo = get_midia_repository()
    return repo.listar_todas()

# 4. Avaliar Mídia
@router.post("/{midia_id}/avaliar", response_model=MidiaResponse)
def avaliar_midia(midia_id: int, avaliacao: AvaliacaoCreate):
    repo = get_midia_repository()
    midia = repo.obter_por_id(midia_id)
    if not midia:
        raise HTTPException(status_code=404, detail="Mídia não encontrada.")

    try:
        midia.avaliar(avaliacao.nota)
        repo.atualizar(midia)
        return midia
    except (ValorInvalidoError, EstadoInvalidoError) as e:
        raise HTTPException(status_code=400, detail=str(e))


# 5. Atualizar Status
@router.patch("/{midia_id}/status", response_model=MidiaResponse)
def atualizar_status(midia_id: int, status_update: StatusUpdate):
    repo = get_midia_repository()
    midia = repo.obter_por_id(midia_id)
    if not midia:
        raise HTTPException(status_code=404, detail="Mídia não encontrada.")

    try:
        if isinstance(midia, Serie):
            midia.atualizar_status()
        else:
            midia.alterar_status(status_update.status)

        repo.atualizar(midia)
        return midia
    except (ValorInvalidoError, EstadoInvalidoError) as e:
        raise HTTPException(status_code=400, detail=str(e))

# 6. Obter Mídia por ID
@router.get("/{midia_id}", response_model=MidiaResponse)
def obter_midia(midia_id: int):
    repo = get_midia_repository()
    midia = repo.obter_por_id(midia_id)
    if not midia:
        raise HTTPException(status_code=404, detail="Mídia não encontrada.")
    return midia

@router.get("/relatorios/notas-por-genero", response_model=Dict[str, float])
def relatorio_notas_por_genero():
    """
    Retorna a média de notas das mídias assistidas agrupadas por gênero.
    """
    # 1. Instancia o repositório (ou use Injeção de Dependência, se já tiver configurado)
    repo = MidiaRepositorySQLite()

    # 2. Carrega todas as mídias do banco de dados
    todas_midias = repo.carregar_todos()

    # 3. Processa o relatório através do serviço
    medias = RelatorioService.media_notas_por_genero(todas_midias)

    # 4. Retorna o dicionário (o FastAPI converte automaticamente para JSON)
    return medias

@router.get("/relatorios/tempo-total-por-tipo", response_model=Dict[str, float])
def relatorio_tempo_total():
    """
    Retorna o tempo total das mídias assistidas agrupadas por tipo.
    """
    repo = get_midia_repository()
    todas_midias = repo.carregar_todos()
    return RelatorioService.tempo_total_assistido_por_tipo(todas_midias)
