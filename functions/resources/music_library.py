"""Parse a Music.app exported Library.xml into per-artist play data.

Output shape is a plain `dict[str, dict]` keyed by Album Artist, sorted by
total play count descending. Kept as raw dicts (not dataclasses) so the
result is trivially JSON-serialisable for inspection/debugging.

The parser knows nothing about Spotify — it only digests the XML.
"""

from __future__ import annotations

import logging
import os
import plistlib
import re
import shutil
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)

# --- Parsing rules (edit these to tweak behaviour) -------------------------

# Album Artist values that mean "this is a compilation" — for these we group
# by the track's own Artist field instead. Compared case-insensitively.
# Add more markers here if you hit other variants (e.g. "VA", "Various").
VARIOUS_ARTISTS_MARKERS = {"various artists"}

# Featured-artist markers, matched inside () or [] in a track title, e.g.
# "Song (feat. X)", "Song [Featuring Y & Z]". Longest alternatives first.
_FEATURED_RE = re.compile(
    r"[\(\[]\s*(?:featuring|feat\.?|ft\.?)\s+(?P<artists>[^)\]]+?)\s*[\)\]]",
    re.IGNORECASE,
)

# Separators used to split the captured string into individual names. The raw
# string is always kept too, so over-splits (e.g. a "X & Y" duo, or "8Ball And
# MJG") are recoverable. Tune this alternation if a particular name keeps
# splitting wrongly.
_FEATURED_SPLIT_RE = re.compile(r"\s*(?:,|&|\band\b)\s*", re.IGNORECASE)


def _extract_featured(title: str) -> str | None:
    """Return the raw featured-artist text from a track title, or None."""
    if not title:
        return None
    match = _FEATURED_RE.search(title)
    if not match:
        return None
    return match.group("artists").strip() or None


def _split_featured(featured: str | None) -> list[str]:
    """Best-effort split of a featured string into individual artist names."""
    if not featured:
        return []
    return [p.strip() for p in _FEATURED_SPLIT_RE.split(featured) if p.strip()]


def _group_artist(raw: dict) -> str:
    """Decide which artist a track is grouped under.

    Normally the Album Artist; but for compilations (Album Artist is a
    "various artists" marker) we fall back to the track's own Artist so the
    real performer is surfaced instead of a meaningless bucket.
    """
    album_artist = (raw.get("Album Artist") or "").strip()
    track_artist = (raw.get("Artist") or "").strip()
    if album_artist.casefold() in VARIOUS_ARTISTS_MARKERS:
        return track_artist or album_artist
    return album_artist or track_artist


# ---------------------------------------------------------------------------

# Repo root: functions/resources/music_library.py -> resources -> functions -> root
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _default_backups_dir() -> Path:
    """Where timestamped library snapshots go.

    Defaults to ``<repo>/dumps/backups``; override with ``LIBRARY_BACKUPS_DIR``
    (needed in Docker, where the code root isn't the repo root).
    """
    raw = os.environ.get("LIBRARY_BACKUPS_DIR")
    if raw:
        return Path(raw).expanduser()
    return _PROJECT_ROOT / "dumps" / "backups"


def snapshot_library(src: Path, backups_dir: Path | None = None) -> Path | None:
    """Copy ``src`` into ``backups_dir`` as a timestamped, gitignored snapshot.

    The filename is keyed on the source file's mtime, so re-parsing the same
    export (e.g. on server restart) is idempotent — it won't pile up duplicate
    copies of an unchanged library. Returns the snapshot path, or None if the
    source is missing or the copy fails (backups are best-effort, never fatal).
    """
    backups_dir = backups_dir or _default_backups_dir()
    try:
        if not src.exists():
            return None
        stamp = datetime.fromtimestamp(src.stat().st_mtime, tz=timezone.utc).strftime(
            "%Y%m%d-%H%M%S"
        )
        backups_dir.mkdir(parents=True, exist_ok=True)
        dest = backups_dir / f"{src.stem}-{stamp}{src.suffix}"
        if dest.exists():
            return dest
        shutil.copy2(src, dest)
        logger.info("Backed up library snapshot -> %s", dest)
        return dest
    except OSError as exc:
        logger.warning("Library snapshot failed (continuing): %s", exc)
        return None


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
    name = track.get("Name", "")
    featured = _extract_featured(name)
    return {
        "name": name,
        "album": track.get("Album", ""),
        "genre": track.get("Genre", ""),
        "year": track.get("Year"),
        "plays": int(track.get("Play Count", 0) or 0),
        "rating": track.get("Rating"),  # 0-100 in iTunes XML
        "loved": bool(track.get("Loved", False)),
        "date_added": _iso(track.get("Date Added")),
        "last_played": _iso(track.get("Play Date UTC")),
        "featured": featured,  # raw captured text, e.g. "Alessia Cara & Khalid"
        "featured_artists": _split_featured(featured),  # best-effort list
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
        album_artist = _group_artist(raw)
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
