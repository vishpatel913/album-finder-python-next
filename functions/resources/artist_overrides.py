"""Inert override stub for the artist resolver.

Not wired into the pipeline yet. The resolver calls `lookup()` and treats
an empty return as "no override, proceed with normal Spotify search".

Two override modes are envisaged once this is activated:

1. `search_as`: Music.app name → alternate name to send to Spotify search.
   Use when Spotify indexes an artist under a different spelling than your
   Music.app library uses, but you still want Spotify to do the lookup.
   Example: `"My Bloody Valentine (Live)" -> "My Bloody Valentine"`.

2. `spotify_id`: Music.app name → Spotify artist ID, bypassing search.
   Use when search returns the wrong artist (e.g. ambiguous names) and you
   want to pin the canonical Spotify entity directly.

To activate, replace the body of `lookup()` with a dict lookup against a
hand-maintained mapping (likely loaded from JSON in this same directory).
"""

from __future__ import annotations


def lookup(album_artist: str) -> dict | None:
    """Return override directives for `album_artist`, or None if no override.

    Shape when populated:
        {"search_as": "alternate name"}    # change the search term
        {"spotify_id": "abc123..."}        # skip search, use this ID directly
    """
    return None
