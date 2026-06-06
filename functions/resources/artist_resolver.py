"""Resolve Music.app Album Artist names to Spotify artist records.

Cached on disk by Music.app artist name. Cache value is a dict:
    {id, display_name, image_url, genres}
keyed off the Spotify artist ID (stable) but indexed by the Music.app
name (what the caller has). Spotify "genres" is the per-artist tag list
used for "vibe" filtering on the FE.

The resolver knows nothing about Music.app — it just maps strings to
Spotify entities.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from resources import artist_overrides

logger = logging.getLogger(__name__)

DEFAULT_CACHE_PATH = Path("./data/spotify_artist_cache.json")


def _empty_entry() -> dict:
    return {
        "id": None,
        "display_name": None,
        "image_url": None,
        "genres": [],
        "spotify_url": None,
        "uri": None,
        "popularity": None,
        "followers": None,
    }


def _normalise_entry(value) -> dict:
    """Migrate legacy {name: id_string} entries to the dict shape on read."""
    if value is None:
        return {**_empty_entry(), "id": None}
    if isinstance(value, str):
        return {**_empty_entry(), "id": value}
    if isinstance(value, dict):
        return {**_empty_entry(), **value}
    return _empty_entry()


class ArtistResolver:
    def __init__(self, spotify_client, cache_path: Path = DEFAULT_CACHE_PATH):
        # spotify_client is the spotipy.Spotify object (not our SpotifySearch wrapper)
        self.spotify = spotify_client
        self.cache_path = Path(cache_path)
        self._cache: dict[str, dict] = self._load_cache()
        self._dirty = False

    def _load_cache(self) -> dict[str, dict]:
        if not self.cache_path.exists():
            return {}
        try:
            with self.cache_path.open("r") as fh:
                raw = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read cache %s: %s — starting fresh", self.cache_path, exc)
            return {}
        return {name: _normalise_entry(value) for name, value in raw.items()}

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

    def get_cached(self, album_artist: str) -> dict | None:
        return self._cache.get(album_artist)

    def resolve(self, album_artist: str) -> dict | None:
        """Return the cached entry for `album_artist`, populating on miss.

        Order: override → cache → Spotify search + hydrate → cache write.
        Returns the full dict (or None on hard miss).
        """
        override = artist_overrides.lookup(album_artist) or {}
        pinned_id = override.get("spotify_id")
        if pinned_id:
            cached = self._cache.get(album_artist)
            if cached and cached.get("id") == pinned_id:
                return cached
            entry = self._fetch_artist_by_id(pinned_id)
            if entry:
                self._cache[album_artist] = entry
                self._dirty = True
            return entry

        cached = self._cache.get(album_artist)
        if cached and cached.get("id"):
            return cached

        search_term = override.get("search_as", album_artist)
        entry = self._search_and_hydrate(search_term)
        # Always record the miss so we don't re-search next time.
        self._cache[album_artist] = entry or _empty_entry()
        self._dirty = True
        return entry

    def resolve_many(self, album_artists: list[str]) -> dict[str, dict | None]:
        """Bulk-resolve. Hits cache first, then Spotify batch-fetches misses.

        Search itself isn't batched (Spotify doesn't expose batch search),
        but the hydrate step uses `artists?ids=...` (up to 50 IDs/call).
        """
        results: dict[str, dict | None] = {}
        needs_search: list[str] = []
        for name in album_artists:
            override = artist_overrides.lookup(name) or {}
            if override.get("spotify_id"):
                cached = self._cache.get(name)
                if cached and cached.get("id") == override["spotify_id"]:
                    results[name] = cached
                else:
                    needs_search.append(name)
                continue
            cached = self._cache.get(name)
            if cached and cached.get("id"):
                results[name] = cached
            else:
                needs_search.append(name)

        for name in needs_search:
            results[name] = self.resolve(name)
        return results

    def _search_and_hydrate(self, query: str) -> dict | None:
        try:
            results = self.spotify.search(q=f"artist:{query}", type="artist", limit=1)
        except Exception as exc:
            logger.warning("Spotify search failed for %r: %s", query, exc)
            return None

        items = results.get("artists", {}).get("items", [])
        if not items:
            logger.info("No Spotify match for %r", query)
            return None

        match = items[0]
        return _entry_from_artist_object(match)

    def _fetch_artist_by_id(self, artist_id: str) -> dict | None:
        try:
            artist = self.spotify.artist(artist_id)
        except Exception as exc:
            logger.warning("Spotify artist(%r) failed: %s", artist_id, exc)
            return None
        return _entry_from_artist_object(artist)


def _entry_from_artist_object(artist: dict) -> dict:
    images = artist.get("images") or []
    image_url = (
        images[1]["url"] if len(images) > 1 else (images[0]["url"] if images else None)
    )
    followers = (artist.get("followers") or {}).get("total")
    return {
        "id": artist.get("id"),
        "display_name": artist.get("name"),
        "image_url": image_url,
        "genres": artist.get("genres", []),
        "spotify_url": (artist.get("external_urls") or {}).get("spotify"),
        "uri": artist.get("uri"),
        "popularity": artist.get("popularity"),
        "followers": followers,
    }
