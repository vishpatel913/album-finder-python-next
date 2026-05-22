"""FastAPI dependency providers.

Holds the singletons (Spotify client, resolver, library cache) and the
mtime-keyed parse cache. Routes pull these via `Depends(...)` so they
stay declarative.
"""

from __future__ import annotations

import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from resources.artist_resolver import ArtistResolver
from resources.music_library import parse_library

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_state: dict = {
    "library_path": None,
    "library_mtime": None,
    "parsed": None,
    "spotify": None,
    "resolver": None,
}


def library_path() -> Path:
    raw = os.environ.get("MUSIC_LIBRARY_XML") or "~/Music/Library.xml"
    return Path(raw).expanduser()


def cache_path() -> Path:
    raw = os.environ.get("SPOTIFY_CACHE_PATH") or "./data/spotify_artist_cache.json"
    return Path(raw).expanduser()


def get_spotify() -> spotipy.Spotify:
    with _lock:
        if _state["spotify"] is None:
            _state["spotify"] = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
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
        parsed = parse_library(path)
        _state["library_path"] = str(path)
        _state["library_mtime"] = mtime
        _state["parsed"] = parsed
        return parsed


def library_mtime_iso() -> str | None:
    mtime = _state.get("library_mtime")
    if mtime is None:
        return None
    return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
