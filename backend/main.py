from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import INFO, basicConfig, getLogger

from api.routes import albums, artists, health, tracks
from fastapi import FastAPI

from database.session import create_db_and_tables

logger = getLogger(__name__)
basicConfig(level=INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up...")
    create_db_and_tables()
    yield
    logger.info("Shutting down...")
    logger.info("Finished shutting down.")


def get_app() -> FastAPI:
    app = FastAPI(title="Music Library API", lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(artists.router)
    app.include_router(albums.router)
    app.include_router(tracks.router)
    return app


app = get_app()
