"""FastAPI entrypoint for the Album Finder local API.

Run from `functions/` with: `uvicorn api.main:app --reload --port 8000`
or via docker compose.
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from api.deps import get_parsed_library, get_resolver, library_mtime_iso, library_path
from api.routes import library as library_routes
from api.routes import spotify as spotify_routes
from api.schemas import Health

app = FastAPI(title="Album Finder", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    # Restricted to the Next dev server. The docker network uses service-name
    # routing (http://api:8000), so the browser never hits FastAPI directly
    # in the docker setup — this is for bare-metal dev only.
    allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(library_routes.router)
app.include_router(spotify_routes.router)


@app.get("/api/health", response_model=Health)
def health() -> Health:
    try:
        parsed = get_parsed_library()
        artists = len(parsed)
    except FileNotFoundError:
        artists = 0
    resolver = get_resolver()
    return Health(
        library_path=str(library_path()),
        library_mtime=library_mtime_iso(),
        artists_parsed=artists,
        cache_entries=len(resolver._cache),  # noqa: SLF001 — diagnostic only
    )
