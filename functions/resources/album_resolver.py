"""Resolve (artist, album) pairs to Spotify album records.

Mirrors ArtistResolver: a disk cache keyed by "artist␟album", populated on
miss via Spotify album search. Cache value:
    {id, name, image_url, release_date, total_tracks, spotify_url, uri}
Misses are recorded (empty entry) so we don't re-search next time.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_KEY_SEP = "␟"  # unit-separator: safe between artist and album


def _empty_entry() -> dict:
    return {
        "id": None,
        "name": None,
        "image_url": None,
        "release_date": None,
        "total_tracks": None,
        "spotify_url": None,
        "uri": None,
    }


def _entry_from_album_object(album: dict) -> dict:
    images = album.get("images") or []
    image_url = (
        images[1]["url"] if len(images) > 1 else (images[0]["url"] if images else None)
    )
    return {
        "id": album.get("id"),
        "name": album.get("name"),
        "image_url": image_url,
        "release_date": album.get("release_date"),
        "total_tracks": album.get("total_tracks"),
        "spotify_url": (album.get("external_urls") or {}).get("spotify"),
        "uri": album.get("uri"),
    }


class AlbumResolver:
    def __init__(self, spotify_client, cache_path: Path):
        self.spotify = spotify_client
        self.cache_path = Path(cache_path)
        self._cache: dict[str, dict] = self._load_cache()
        self._dirty = False

    @staticmethod
    def _key(artist: str, album: str) -> str:
        return f"{artist}{_KEY_SEP}{album}"

    def _load_cache(self) -> dict[str, dict]:
        if not self.cache_path.exists():
            return {}
        try:
            with self.cache_path.open("r") as fh:
                raw = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read album cache %s: %s — starting fresh", self.cache_path, exc)
            return {}
        return {k: {**_empty_entry(), **v} for k, v in raw.items()}

    def save(self) -> None:
        if not self._dirty:
            return
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.cache_path.with_suffix(".json.tmp")
        with tmp.open("w") as fh:
            json.dump(self._cache, fh, indent=2, sort_keys=True)
        os.replace(tmp, self.cache_path)
        logger.info("Saved album cache (%d entries) to %s", len(self._cache), self.cache_path)
        self._dirty = False

    def get_cached(self, artist: str, album: str) -> dict | None:
        return self._cache.get(self._key(artist, album))

    def resolve(self, artist: str, album: str) -> dict | None:
        cached = self.get_cached(artist, album)
        if cached and cached.get("id"):
            return cached
        entry = self._search(artist, album)
        self._cache[self._key(artist, album)] = entry or _empty_entry()
        self._dirty = True
        return entry

    def resolve_many(self, pairs: list[tuple[str, str]]) -> dict[tuple[str, str], dict | None]:
        results: dict[tuple[str, str], dict | None] = {}
        needs: list[tuple[str, str]] = []
        for artist, album in pairs:
            cached = self.get_cached(artist, album)
            if cached and cached.get("id"):
                results[(artist, album)] = cached
            else:
                needs.append((artist, album))

        total = len(needs)
        if total:
            logger.info("Spotify album enrich: %d cached, %d to fetch", len(results), total)
        for i, (artist, album) in enumerate(needs, 1):
            entry = self.resolve(artist, album)
            results[(artist, album)] = entry
            mark = f"✓ {entry['name']}" if entry and entry.get("id") else "✗ no match"
            logger.info("  [%d/%d] %s — %s → %s", i, total, artist, album, mark)
        return results

    def _search(self, artist: str, album: str) -> dict | None:
        query = f"album:{album} artist:{artist}"
        try:
            results = self.spotify.search(q=query, type="album", limit=1)
        except Exception as exc:  # noqa: BLE001 — fail soft, same as ArtistResolver
            logger.warning("Spotify album search failed for %r — %r: %s", artist, album, exc)
            return None
        items = results.get("albums", {}).get("items", [])
        if not items:
            logger.info("No Spotify album match for %r — %r", artist, album)
            return None
        return _entry_from_album_object(items[0])
