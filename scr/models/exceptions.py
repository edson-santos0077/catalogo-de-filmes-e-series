class DominioError(Exception):
    """Exceção base para regras de negócio do sistema."""
    pass

class ValorInvalidoError(DominioError, ValueError):
    """Lançada quando um parâmetro numérico ou string violar validações."""
    pass

class EstadoInvalidoError(DominioError, ValueError):
    """Lançada quando houver uma transição de estado não permitida."""
    pass
