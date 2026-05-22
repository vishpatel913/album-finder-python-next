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
from collections import defaultdict
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)


def _normalise(name: str) -> str:
    # NFKD + ASCII fold strips accents; casefold + whitespace collapse
    # catches the "Beyoncé" vs "Beyonce" / "  Radiohead " kind of dupes.
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_only.casefold().split())


def parse_library(
    xml_path: Path,
    *,
    min_track_plays: int = 0,
    min_artist_plays: int = 0,
) -> dict[str, dict]:
    """Parse Music.app Library.xml → {album_artist: {total_plays, tracks}}.

    Filters are applied in order: tracks below `min_track_plays` are dropped
    first, then artists whose surviving track total falls below
    `min_artist_plays`. The returned dict is insertion-sorted by total plays
    descending.
    """
    xml_path = Path(xml_path).expanduser()
    if not xml_path.exists():
        raise FileNotFoundError(f"Library XML not found: {xml_path}")

    with xml_path.open("rb") as fh:
        library = plistlib.load(fh)

    raw_tracks = library.get("Tracks", {})
    grouped: dict[str, list[dict]] = defaultdict(list)

    for track in raw_tracks.values():
        album_artist = (track.get("Album Artist") or track.get("Artist") or "").strip()
        if not album_artist:
            continue

        plays = int(track.get("Play Count", 0) or 0)
        if plays < min_track_plays:
            continue

        grouped[album_artist].append({
            "name": track.get("Name", ""),
            "album": track.get("Album", ""),
            "plays": plays,
        })

    aggregated: list[tuple[str, dict]] = []
    for album_artist, tracks in grouped.items():
        total = sum(t["plays"] for t in tracks)
        if total < min_artist_plays:
            continue
        aggregated.append((album_artist, {
            "total_plays": total,
            "track_count": len(tracks),
            "tracks": tracks,
        }))

    aggregated.sort(key=lambda item: item[1]["total_plays"], reverse=True)
    logger.info("Parsed %d artists from %s", len(aggregated), xml_path)
    return dict(aggregated)


def find_near_duplicate_artists(album_artists: Iterable[str]) -> list[list[str]]:
    """Return groups of Album Artist names that collapse to the same form.

    Surfaces case/whitespace/accent variants of the same artist so the user
    can clean them up in Music.app. Only returns groups with 2+ members.
    """
    buckets: dict[str, list[str]] = defaultdict(list)
    for name in album_artists:
        buckets[_normalise(name)].append(name)

    return [sorted(set(names)) for names in buckets.values() if len({*names}) > 1]
