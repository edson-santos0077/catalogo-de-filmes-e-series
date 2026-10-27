from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.events import EventDispatcher
from src.core.loggers import ConsoleLogger, FileLogger
# Importe as suas rotas
from src.api.rotas_midias import router as rotas_midias
from src.api.rotas_usuarios import router as rotas_usuarios

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Regista os observadores antes de a API começar a receber requisições
    dispatcher = EventDispatcher()
    dispatcher.inscrever(ConsoleLogger())
    dispatcher.inscrever(FileLogger())

    # Guarda o dispatcher no estado da app para o usar nas rotas, se necessário
    app.state.dispatcher = dispatcher

    yield  # A API fica em execução neste ponto

    # 2. Quando a API for desligada, o código continua aqui
    print("Encerrando a API...")

# 3. Criação da instância FastAPI
app = FastAPI(
    title="Catálogo de Mídias API",
    description="API para gestão de filmes, séries e listas de utilizadores.",
    version="1.0.0",
    lifespan=lifespan
)

# 4. Registar as rotas que construiu
app.include_router(rotas_midias)
app.include_router(rotas_usuarios)

@app.get("/")
def root():
    return {"status": "ok", "mensagem": "API de Catálogos ativa."}
