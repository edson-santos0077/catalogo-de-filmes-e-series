from enum import Enum

class StatusVisualizacao(Enum):
    """
    Enumeração que representa o estado de visualização de uma mídia ou episódio.
    """
    NAO_ASSISTIDO = "NAO_ASSISTIDO"
    ASSISTINDO = "ASSISTINDO"
    ASSISTIDO = "ASSISTIDO"

class TipoMidia(Enum):
    """
    Enumeração que define os tipos de mídia suportados pelo catálogo.
    """
    FILME = "FILME"
    SERIE = "SERIE"
