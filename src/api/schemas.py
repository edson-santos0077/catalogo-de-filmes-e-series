from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from src.models.enums import TipoMidia, StatusVisualizacao

class MidiaBase(BaseModel):
    titulo: str = Field(..., min_length=1)
    tipo: TipoMidia
    genero: str = Field(..., min_length=1)
    ano: int = Field(..., gt=1800)
    classificacao_indicativa: str
    elenco: Optional[List[str]] = []

class MidiaCreate(MidiaBase):
    duracao_minutos: Optional[int] = Field(None, description="Obrigatório para filmes")

class MidiaResponse(MidiaBase):
    id: int | None = None
    status: StatusVisualizacao
    nota: Optional[float] = None

    class Config:
        from_attributes = True

class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=2)
    email: EmailStr

class UsuarioResponse(BaseModel):
    id_usuario: str | int | None = None
    nome: str
    email: str
    limite_listas: int

    class Config:
        from_attributes = True

class AvaliacaoCreate(BaseModel):
    nota: float = Field(..., ge=0.0, le=10.0, description="Nota de 0 a 10")

class EpisodioCreate(BaseModel):
    numero_temporada: int = Field(..., gt=0)
    numero_episodio: int = Field(..., gt=0)
    titulo: str = Field(..., min_length=1)
    duracao_minutos: int = Field(..., gt=0)
    data_lancamento: Optional[str] = None

class StatusUpdate(BaseModel):
    status: StatusVisualizacao

class ListaCreate(BaseModel):
    nome: str = Field(..., min_length=1)

class FavoritoCreate(BaseModel):
    midia_id: int
