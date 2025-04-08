from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import game_manager
from .routes import game, login_system
from .config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    manager = game_manager.GameManager(get_settings())
    manager.setup_database()

    app.state.game_manager = manager

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(login_system.router, tags=["login"])
app.include_router(game.router, tags=["game"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
