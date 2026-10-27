from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.events import EventDispatcher
from src.core.loggers import ConsoleLogger, FileLogger

# Importar os routers da API
from src.api.rotas_midias import router as rotas_midias
from src.api.rotas_usuarios import router as rotas_usuarios

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: Regista os observadores antes de rodar a API
    dispatcher = EventDispatcher()
    dispatcher.inscrever(ConsoleLogger())
    dispatcher.inscrever(FileLogger())

    # Guarda o dispatcher no estado da aplicação para uso nas rotas
    app.state.dispatcher = dispatcher

    yield  # A API fica em execução neste ponto

    # SHUTDOWN: Lógica de encerramento (fechar conexões de banco de dados, fechar arquivos de log, etc.)
    print("Encerrando a API...")

app = FastAPI(
    title="Catálogo de Mídias API",
    description="API para gestão de filmes, séries e listas de utilizadores.",
    version="1.0.0",
    lifespan=lifespan
)

# Registar as rotas
# app.include_router(rotas_midias, prefix="/midias", tags=["Mídias"])
# app.include_router(rotas_usuarios, prefix="/usuarios", tags=["Usuários"])

@app.get("/")
def root():
    return {"status": "ok", "mensagem": "API de Catálogos ativa."}
