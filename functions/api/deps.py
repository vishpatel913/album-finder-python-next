"""FastAPI dependency providers.

Holds the singletons (Spotify client, resolver, library cache) and the
mtime-keyed parse cache. Routes pull these via `Depends(...)` so they
stay declarative.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

import spotipy
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyClientCredentials

from resources.artist_resolver import ArtistResolver
from resources.music_library import parse_library, snapshot_library

logger = logging.getLogger(__name__)

# Network calls to Spotify time out instead of hanging forever (spotipy/requests
# default to no timeout). Token fetch + searches respect this.
SPOTIFY_REQUEST_TIMEOUT = 10  # seconds


class SpotifyCredentialsError(RuntimeError):
    """Raised when Spotify creds are missing — surfaced as a clean 503."""

# Repo root: functions/api/deps.py -> functions/api -> functions -> root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
# Default local dump location (gitignored). Drop your Music.app
# Library.xml export here and the app builds from it automatically.
DEFAULT_LIBRARY_PATH = PROJECT_ROOT / "dumps" / "Library.xml"

# Reentrant: get_resolver() holds the lock and calls get_spotify(), which
# re-acquires it. A plain Lock here self-deadlocks the whole resolver path.
_lock = threading.RLock()
_state: dict = {
    "library_path": None,
    "library_mtime": None,
    "parsed": None,
    "spotify": None,
    "resolver": None,
}


def library_path() -> Path:
    """Resolve the Library.xml path.

    Uses ``MUSIC_LIBRARY_XML`` if set, otherwise defaults to the gitignored
    ``dumps/Library.xml`` at the repo root. Relative paths (from the env var)
    resolve against the project root, not the current working directory, so it
    works whether you launch uvicorn from ``functions/`` or the repo root.
    """
    raw = os.environ.get("MUSIC_LIBRARY_XML")
    if not raw:
        return DEFAULT_LIBRARY_PATH
    path = Path(raw).expanduser()
    return path if path.is_absolute() else (PROJECT_ROOT / path)


def cache_path() -> Path:
    """Spotify artist cache path.

    Defaults to the gitignored repo-root ``data/`` folder. Relative paths
    resolve against the project root, not the cwd — otherwise running uvicorn
    from ``functions/`` writes the cache (and the token cache beside it) to an
    un-gitignored ``functions/data/``, risking committing an access token.
    """
    raw = os.environ.get("SPOTIFY_CACHE_PATH") or "data/spotify_artist_cache.json"
    path = Path(raw).expanduser()
    return path if path.is_absolute() else (PROJECT_ROOT / path)


def get_spotify() -> spotipy.Spotify:
    with _lock:
        if _state["spotify"] is None:
            if not (
                os.environ.get("SPOTIPY_CLIENT_ID")
                and os.environ.get("SPOTIPY_CLIENT_SECRET")
            ):
                raise SpotifyCredentialsError(
                    "Spotify credentials missing — set SPOTIPY_CLIENT_ID and "
                    "SPOTIPY_CLIENT_SECRET in your .env at the repo root."
                )
            # Keep spotipy's token cache out of the cwd; park it beside the
            # artist cache (gitignored) instead of dropping a `.cache` file.
            token_cache = cache_path().parent / ".spotify-token-cache"
            token_cache.parent.mkdir(parents=True, exist_ok=True)
            auth = SpotifyClientCredentials(
                cache_handler=CacheFileHandler(cache_path=str(token_cache))
            )
            _state["spotify"] = spotipy.Spotify(
                auth_manager=auth,
                requests_timeout=SPOTIFY_REQUEST_TIMEOUT,
                retries=2,
            )
        return _state["spotify"]


def get_resolver() -> ArtistResolver:
    with _lock:
        if _state["resolver"] is None:
            _state["resolver"] = ArtistResolver(get_spotify(), cache_path=cache_path())
        return _state["resolver"]


def get_parsed_library(force: bool = False) -> dict:
    """Return the parsed library, re-parsing if the XML's mtime changed.

    Holds the result in process memory keyed by mtime so repeated requests
    don't re-parse. `force=True` from the /refresh endpoint invalidates.
    """
    path = library_path()
    if not path.exists():
        raise FileNotFoundError(f"Library XML not found at {path}")
    mtime = path.stat().st_mtime

    with _lock:
        cached_mtime = _state["library_mtime"]
        if not force and _state["parsed"] is not None and cached_mtime == mtime:
            return _state["parsed"]

        logger.info("Parsing %s (mtime=%s)", path, mtime)
        snapshot_library(path)
        parsed = parse_library(path)
        _state["library_path"] = str(path)
        _state["library_mtime"] = mtime
        _state["parsed"] = parsed
        return parsed


def cache_entry_count() -> int:
    """Count cached Spotify entries WITHOUT constructing the Spotify client.

    Used by /api/health. Constructing the client (`get_resolver`) hangs ~20s
    when Spotify creds are missing, so health must never go through it. If the
    resolver already exists we use its in-memory cache; otherwise we read the
    cache file directly.
    """
    resolver = _state.get("resolver")
    if resolver is not None:
        return len(resolver._cache)  # noqa: SLF001 — diagnostic only
    path = cache_path()
    if not path.exists():
        return 0
    try:
        with path.open("r") as fh:
            return len(json.load(fh))
    except (json.JSONDecodeError, OSError):
        return 0


def library_mtime_iso() -> str | None:
    mtime = _state.get("library_mtime")
    if mtime is None:
        return None
    return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
