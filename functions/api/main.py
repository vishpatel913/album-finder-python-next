"""FastAPI entrypoint for the Album Finder local API.

Run from `functions/` with: `uvicorn api.main:app --reload --port 8000`
or via docker compose.
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 10):
    raise RuntimeError(
        f"Album Finder requires Python 3.10+, but you're on "
        f"{sys.version_info.major}.{sys.version_info.minor}. "
        "The code uses `X | None` union syntax (PEP 604). "
        "Recreate the venv with Python 3.10+ — e.g. macOS system python3 is 3.9 and will not work."
    )

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOauthError

from api.deps import (
    SpotifyCredentialsError,
    cache_entry_count,
    get_parsed_library,
    library_mtime_iso,
    library_path,
)
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

@app.exception_handler(SpotifyCredentialsError)
def _handle_missing_creds(request: Request, exc: SpotifyCredentialsError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(SpotifyOauthError)
def _handle_oauth_error(request: Request, exc: SpotifyOauthError) -> JSONResponse:
    return JSONResponse(
        status_code=503, content={"detail": f"Spotify auth failed: {exc}"}
    )


@app.exception_handler(SpotifyException)
def _handle_spotify_error(request: Request, exc: SpotifyException) -> JSONResponse:
    # e.g. rate limit, upstream 5xx, or a request timeout we now enforce.
    return JSONResponse(
        status_code=503, content={"detail": f"Spotify API error: {exc}"}
    )


app.include_router(library_routes.router)
app.include_router(spotify_routes.router)


@app.get("/api/health", response_model=Health)
def health() -> Health:
    path = library_path()
    # Cache count is read cheaply (no Spotify client — that hangs ~20s when
    # creds are missing). The library parse is cached after the first hit.
    try:
        artists = len(get_parsed_library())
    except FileNotFoundError:
        artists = 0
    return Health(
        status="ok",
        library_path=str(path),
        library_exists=path.exists(),
        library_mtime=library_mtime_iso(),
        artists_parsed=artists,
        cache_entries=cache_entry_count(),
    )
