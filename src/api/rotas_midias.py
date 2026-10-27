from typing import List
from fastapi import APIRouter, HTTPException, status

from src.api.schemas import (
    MidiaCreate, MidiaResponse, AvaliacaoCreate, EpisodioCreate, StatusUpdate
)
from src.models.filme import Filme
from src.models.serie import Serie, Temporada, Episodio
from src.models.enums import TipoMidia
from src.models.exceptions import ValorInvalidoError, EstadoInvalidoError
from src.repositories.database import get_midia_repository

router = APIRouter(prefix="/midias", tags=["Mídias"])

# 1. Adicionar Mídia
@router.post("/", response_model=MidiaResponse, status_code=status.HTTP_201_CREATED)
def criar_midia(midia_in: MidiaCreate):
    repo = get_midia_repository()

    try:
        if midia_in.tipo == TipoMidia.FILME:
            if not midia_in.duracao_minutos:
                raise HTTPException(status_code=400, detail="Filmes exigem a duração em minutos.")
            nova_midia = Filme(
                titulo=midia_in.titulo,
                genero=midia_in.genero,
                ano=midia_in.ano,
                classificacao_indicativa=midia_in.classificacao_indicativa,
                elenco=midia_in.elenco,
                duracao_minutos=midia_in.duracao_minutos
            )
        else:
            nova_midia = Serie(
                titulo=midia_in.titulo,
                genero=midia_in.genero,
                ano=midia_in.ano,
                classificacao_indicativa=midia_in.classificacao_indicativa,
                elenco=midia_in.elenco
            )

        midia_salva = repo.adicionar(nova_midia)
        return midia_salva
    except (ValorInvalidoError, EstadoInvalidoError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Erro ao criar mídia: " + str(e))

# 2. Relatório Top 10 (Deve vir antes do GET /{midia_id})
@router.get("/relatorios/top", response_model=List[MidiaResponse])
def relatorio_top_midias():
    repo = get_midia_repository()
    todas_midias = repo.listar_todas()
    avaliadas = [m for m in todas_midias if getattr(m, 'nota', None) is not None]
    top_10 = sorted(avaliadas, key=lambda x: x.nota, reverse=True)[:10]
    return top_10

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

# 5. Adicionar Episódio a Série
@router.post("/{midia_id}/episodios", response_model=MidiaResponse)
def adicionar_episodio(midia_id: int, ep_in: EpisodioCreate):
    repo = get_midia_repository()
    serie = repo.obter_por_id(midia_id)

    if not serie or not isinstance(serie, Serie):
        raise HTTPException(status_code=404, detail="Série não encontrada ou a mídia não é uma série.")

    try:
        novo_episodio = Episodio(
            numero_temporada=ep_in.numero_temporada,
            numero_episodio=ep_in.numero_episodio,
            titulo=ep_in.titulo,
            duracao_minutos=ep_in.duracao_minutos,
            data_lancamento=ep_in.data_lancamento
        )

        temporada = next((t for t in serie.temporadas if t.numero == ep_in.numero_temporada), None)
        if not temporada:
            temporada = Temporada(ep_in.numero_temporada)
            serie.adicionar_temporada(temporada)

        temporada.adicionar_episodio(novo_episodio)
        repo.atualizar(serie)
        return serie
    except (ValorInvalidoError, EstadoInvalidoError) as e:
        raise HTTPException(status_code=400, detail=str(e))

# 6. Atualizar Status
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

# 7. Obter Mídia por ID
@router.get("/{midia_id}", response_model=MidiaResponse)
def obter_midia(midia_id: int):
    repo = get_midia_repository()
    midia = repo.obter_por_id(midia_id)
    if not midia:
        raise HTTPException(status_code=404, detail="Mídia não encontrada.")
    return midia
