from __future__ import annotations

import hashlib
import logging
import plistlib
from datetime import datetime
from pathlib import Path
import re
from typing import Optional
import unicodedata

from utils.unique import unique_by
from sqlalchemy import Null

logger = logging.getLogger(__name__)


def _iso(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)

def _slugify(name: str, extension: str = None) -> str:
    base = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-z0-9]+", "-", base.strip().lower()).strip("-")
    digest = hashlib.sha1(name.encode()).hexdigest()[:6]   # stable per input

    if extension:
        ext = unicodedata.normalize("NFKD", extension).encode("ascii", "ignore").decode()
        ext = re.sub(r"[^a-z0-9]+", "-", ext.strip().lower()).strip("-")
    
        return f"{base}-{ext}-{digest}"          # "p-nk-a1b2c3", "made-in-the-manor-9f8e7d"
    
    return f"{base}-{digest}"          # "p-nk-a1b2c3", "made-in-the-manor-9f8e7d"


def _music_library_track(track: dict) -> dict:
    name = track.get("Name", "")
    # featured = _extract_featured(name)
    return {
        "id": track.get("Persistent ID", ""),
        "name": name,
        "artist": track.get("Artist", ""),
        "album_artist": track.get("Album Artist", ""),
        "album": track.get("Album", ""),
        "genre": track.get("Genre", ""),
        "year": track.get("Year"),
        "track_id": int(track.get("Track ID", 0)) or Null,
        "track_number": int(track.get("Track Number", 0)) or Null,
        "track_length": int(track.get("Total Time", 0) or 0),
        "date_added": _iso(track.get("Date Added")),
        "last_played": _iso(track.get("Play Date UTC")),
        "play_count": int(track.get("Play Count", 0) or 0),
        "album_rating": track.get("Album Rating"),  # 0-100 in iTunes XML
        "album_rating_computed": track.get(
            "Album Rating Computed"
        ),  # 0-100 in iTunes XML
        "compilation": bool(track.get("Compilation", False)),
    }

def _album_dict(track: dict) -> dict:
    album = track.get("album", "")
    album_artist = track.get("album_artist", "")
    id = _slugify(album_artist, album)
    return {
        "id": id,
        "artist": album_artist,
        "album": album,
        "genre": track.get("genre", ""),
        "year": track.get("year"),
        "album_rating": track.get("album_rating"),  # 0-100 in iTunes XML
        "album_rating_computed": track.get("album_rating_computed"),  # 0-100
        "compilation": bool(track.get("compilation", False)),
    }

def _artist_dict(track: dict) -> dict:
    artist = track.get("album_artist", "")
    id = _slugify(artist)
    return {
        "id": id,
        "artist": artist,
    }

def parse_library(
    xml_path: Path,
) -> list[dict]:
    xml_path = Path(xml_path).expanduser()
    if not xml_path.exists():
        raise FileNotFoundError(f"Library XML not found: {xml_path}")

    with xml_path.open("rb") as fh:
        library = plistlib.load(fh)

    raw_tracks = library.get("Tracks", {})
    result: list[dict] = []

    for raw in raw_tracks.values():
        track = _music_library_track(raw)

        result.append(track)

    return result

def extract_albums(parsed_tracks: list[dict]) -> list[dict]:
    albums = (_album_dict(t) for t in parsed_tracks if t.get("album"))
    return unique_by(albums, key=lambda a: a["id"])


def extract_artists(parsed_tracks: list[dict]) -> list[dict]:
    artists = (_artist_dict(t) for t in parsed_tracks if t.get("album_artist"))
    return unique_by(artists, key=lambda a: a["id"])


