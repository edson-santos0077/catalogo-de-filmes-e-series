from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.events import EventDispatcher
from src.core.loggers import ConsoleLogger, FileLogger
from src.api.rotas_midias import router as rotas_midias
from src.api.rotas_usuarios import router as rotas_usuarios

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Regista os observadores no arranque da API
    dispatcher = EventDispatcher()
    dispatcher.inscrever(ConsoleLogger())
    dispatcher.inscrever(FileLogger())

    app.state.dispatcher = dispatcher
    yield
    print("Encerrando a API...")

app = FastAPI(
    title="Catálogo de Mídias API",
    description="API para gestão de filmes, séries e listas de utilizadores.",
    version="1.0.0",
    lifespan=lifespan
)

# Inclui as rotas
app.include_router(rotas_midias)
app.include_router(rotas_usuarios)

@app.get("/")
def root():
    return {"status": "ok", "mensagem": "API de Catálogos ativa."}
