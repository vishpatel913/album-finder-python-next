"""Reduce data/TestLibrary.xml down to a small set of test tracks.

Selections (matched on the Album Artist key, case-insensitive, '!' stripped so
p!nk == pink):
  - 2 highest-play-count tracks each for: kano, haim, kendrick lamar, pond,
    pink, oasis
  - 1 highest-play-count track each from the spiderverse / umbrella academy /
    begin again soundtracks
  - 1 highest-play-count track with genre "Top 40"

All top-level library metadata is preserved; only the Tracks rows are reduced,
and Playlist Items are filtered to the retained tracks so they stay valid.
"""

from __future__ import annotations

import plistlib
import re
from pathlib import Path

SRC = Path("data/TestLibrary.xml")
OUT = Path("data/TestLibrary.reduced.xml")


def norm(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def play_count(track: dict) -> int:
    return int(track.get("Play Count", 0) or 0)


# Album-artist matchers -> how many tracks to keep
ARTIST_RULES = {
    "kano": (lambda n: n == "kano", 2),
    "haim": (lambda n: n == "haim", 2),
    "kendrick lamar": (lambda n: n.startswith("kendrick"), 2),
    "pond": (lambda n: n == "pond", 2),
    "pink (p!nk)": (lambda n: n in {"pink", "pnk"}, 2),
    "oasis": (lambda n: n == "oasis", 2),
}

# Album matchers -> how many tracks to keep
ALBUM_RULES = {
    "into the spiderverse soundtrack": (lambda n: "spiderverse" in n, 1),
    "umbrella academy soundtrack": (lambda n: "umbrellaacademy" in n, 1),
    "begin again soundtrack": (lambda n: "beginagain" in n, 1),
}


def pick(tracks: list[tuple], predicate, key_field: str, n: int, label: str):
    """Return the n highest-play-count (track_key, track) pairs matching predicate."""
    matches = [
        (k, t) for k, t in tracks if predicate(norm(t.get(key_field, "")))
    ]
    matches.sort(key=lambda kt: play_count(kt[1]), reverse=True)
    chosen = matches[:n]
    print(f"\n{label}: {len(matches)} candidate(s), keeping {len(chosen)}")
    for k, t in chosen:
        print(
            f"  [{play_count(t):>4} plays] {t.get('Album Artist','')!r} - "
            f"{t.get('Name','')!r} ({t.get('Album','')!r}, genre={t.get('Genre','')!r})"
        )
    return chosen


def main() -> None:
    lib = plistlib.load(SRC.open("rb"))
    tracks = list(lib["Tracks"].items())  # list of (key, track_dict)
    print(f"loaded {len(tracks)} tracks from {SRC}")

    keep: dict[str, dict] = {}

    for label, (pred, n) in ARTIST_RULES.items():
        for k, t in pick(tracks, pred, "Album Artist", n, f"ARTIST {label}"):
            keep[k] = t

    for label, (pred, n) in ALBUM_RULES.items():
        for k, t in pick(tracks, pred, "Album", n, f"ALBUM {label}"):
            keep[k] = t

    for k, t in pick(tracks, lambda n: n == "top40", "Genre", 1, "GENRE Top 40"):
        keep[k] = t

    # Retained iTunes Track IDs, to prune playlist references.
    kept_track_ids = {int(t.get("Track ID", -1)) for t in keep.values()}
    print(f"\nretained {len(keep)} unique tracks")

    lib["Tracks"] = keep

    # Keep playlists but drop items pointing at removed tracks.
    for pl in lib.get("Playlists", []):
        items = pl.get("Playlist Items")
        if items:
            pl["Playlist Items"] = [
                it for it in items if it.get("Track ID") in kept_track_ids
            ]

    plistlib.dump(lib, OUT.open("wb"))
    print(f"\nwrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
