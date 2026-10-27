import json
from pathlib import Path
from src.core.events import Observer, Evento

class ConsoleLogger(Observer):
    """Exibe eventos formatados no console."""
    def notificar(self, evento: Evento) -> None:
        data_str = evento.data_hora.strftime("%Y-%m-%d %H:%M:%S")
        print(f"📢 [{data_str}] [EVENTO: {evento.nome}] -> {evento.dados}")


class FileLogger(Observer):
    """Persiste logs de eventos em arquivo local de auditoria."""
    def __init__(self, caminho_arquivo: str = "data/eventos.log"):
        self.caminho = Path(caminho_arquivo)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)

    def notificar(self, evento: Evento) -> None:
        registro = {
            "timestamp": evento.data_hora.isoformat(),
            "evento": evento.nome,
            "detalhes": evento.dados
        }
        with open(self.caminho, "a", encoding="utf-8") as f:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")
