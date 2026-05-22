"""Parse a Music.app exported Library.xml into per-artist play data.

Output shape is a plain `dict[str, dict]` keyed by Album Artist, sorted by
total play count descending. Kept as raw dicts (not dataclasses) so the
result is trivially JSON-serialisable for inspection/debugging.

The parser knows nothing about Spotify — it only digests the XML.
"""

from __future__ import annotations

import logging
import plistlib
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)


def _normalise(name: str) -> str:
    # NFKD + ASCII fold strips accents; casefold + whitespace collapse
    # catches the "Beyoncé" vs "Beyonce" / "  Radiohead " kind of dupes.
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_only.casefold().split())


def _iso(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _track_dict(track: dict) -> dict:
    return {
        "name": track.get("Name", ""),
        "album": track.get("Album", ""),
        "genre": track.get("Genre", ""),
        "year": track.get("Year"),
        "plays": int(track.get("Play Count", 0) or 0),
        "rating": track.get("Rating"),  # 0-100 in iTunes XML
        "loved": bool(track.get("Loved", False)),
        "date_added": _iso(track.get("Date Added")),
        "last_played": _iso(track.get("Play Date UTC")),
    }


def parse_library(
    xml_path: Path,
    *,
    min_track_plays: int = 0,
    min_artist_plays: int = 0,
) -> dict[str, dict]:
    """Parse Music.app Library.xml → {album_artist: {total_plays, tracks, ...}}.

    Filters are applied in order: tracks below `min_track_plays` are dropped
    first, then artists whose surviving track total falls below
    `min_artist_plays`. The returned dict is insertion-sorted by total plays
    descending.

    Per-artist rollups added: `top_genre`, `year_min`/`year_max`,
    `date_added_first`/`date_added_last`, `avg_rating`. Per-track detail
    preserved for track-level filtering downstream.
    """
    xml_path = Path(xml_path).expanduser()
    if not xml_path.exists():
        raise FileNotFoundError(f"Library XML not found: {xml_path}")

    with xml_path.open("rb") as fh:
        library = plistlib.load(fh)

    raw_tracks = library.get("Tracks", {})
    grouped: dict[str, list[dict]] = defaultdict(list)

    for raw in raw_tracks.values():
        album_artist = (raw.get("Album Artist") or raw.get("Artist") or "").strip()
        if not album_artist:
            continue

        track = _track_dict(raw)
        if track["plays"] < min_track_plays:
            continue

        grouped[album_artist].append(track)

    aggregated: list[tuple[str, dict]] = []
    for album_artist, tracks in grouped.items():
        total = sum(t["plays"] for t in tracks)
        if total < min_artist_plays:
            continue
        aggregated.append((album_artist, _artist_rollup(tracks, total)))

    aggregated.sort(key=lambda item: item[1]["total_plays"], reverse=True)
    logger.info("Parsed %d artists from %s", len(aggregated), xml_path)
    return dict(aggregated)


def _artist_rollup(tracks: list[dict], total_plays: int) -> dict:
    genres = Counter(t["genre"] for t in tracks if t["genre"])
    years = [t["year"] for t in tracks if isinstance(t["year"], int)]
    dates = sorted(t["date_added"] for t in tracks if t["date_added"])
    ratings = [t["rating"] for t in tracks if isinstance(t["rating"], int) and t["rating"] > 0]

    return {
        "total_plays": total_plays,
        "track_count": len(tracks),
        "top_genre": genres.most_common(1)[0][0] if genres else None,
        "all_genres": sorted(genres.keys()),
        "year_min": min(years) if years else None,
        "year_max": max(years) if years else None,
        "date_added_first": dates[0] if dates else None,
        "date_added_last": dates[-1] if dates else None,
        "avg_rating": round(sum(ratings) / len(ratings), 1) if ratings else None,
        "loved_count": sum(1 for t in tracks if t["loved"]),
        "tracks": tracks,
    }


def find_near_duplicate_artists(album_artists: Iterable[str]) -> list[list[str]]:
    """Return groups of Album Artist names that collapse to the same form.

    Surfaces case/whitespace/accent variants of the same artist so the user
    can clean them up in Music.app. Only returns groups with 2+ members.
    """
    buckets: dict[str, list[str]] = defaultdict(list)
    for name in album_artists:
        buckets[_normalise(name)].append(name)

    return [sorted(set(names)) for names in buckets.values() if len({*names}) > 1]
