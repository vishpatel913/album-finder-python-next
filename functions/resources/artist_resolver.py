"""Resolve Music.app Album Artist names to Spotify artist IDs.

Cached on disk by **Spotify artist ID** (stable), not by raw search response
(volatile). The cache lives at `data/spotify_artist_cache.json` and is
written back atomically at end of run.

The resolver knows nothing about Music.app — it just maps strings to IDs.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from resources import artist_overrides

logger = logging.getLogger(__name__)

DEFAULT_CACHE_PATH = Path("./data/spotify_artist_cache.json")


class ArtistResolver:
    def __init__(self, spotify_client, cache_path: Path = DEFAULT_CACHE_PATH):
        self.spotify = spotify_client
        self.cache_path = Path(cache_path)
        self._cache: dict[str, str | None] = self._load_cache()
        self._dirty = False

    def _load_cache(self) -> dict[str, str | None]:
        if not self.cache_path.exists():
            return {}
        try:
            with self.cache_path.open("r") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read cache %s: %s — starting fresh", self.cache_path, exc)
            return {}

    def save(self) -> None:
        if not self._dirty:
            return
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.cache_path.with_suffix(".json.tmp")
        with tmp.open("w") as fh:
            json.dump(self._cache, fh, indent=2, sort_keys=True)
        os.replace(tmp, self.cache_path)
        logger.info("Saved artist cache (%d entries) to %s", len(self._cache), self.cache_path)
        self._dirty = False

    def resolve(self, album_artist: str) -> str | None:
        """Return a Spotify artist ID for `album_artist`, or None if unresolvable.

        Order: override → cache → Spotify search → cache miss recorded.
        """
        override = artist_overrides.lookup(album_artist)
        if override and override.get("spotify_id"):
            return override["spotify_id"]

        if album_artist in self._cache:
            return self._cache[album_artist]

        search_term = (override or {}).get("search_as", album_artist)
        artist_id = self._search(search_term)
        self._cache[album_artist] = artist_id
        self._dirty = True
        return artist_id

    def _search(self, query: str) -> str | None:
        try:
            results = self.spotify.search(q=f"artist:{query}", type="artist", limit=1)
        except Exception as exc:  # spotipy raises a variety of types
            logger.warning("Spotify search failed for %r: %s", query, exc)
            return None

        items = results.get("artists", {}).get("items", [])
        if not items:
            logger.info("No Spotify match for %r", query)
            return None

        match = items[0]
        logger.info("Resolved %r → %s (%s)", query, match["name"], match["id"])
        return match["id"]
