"""One-time Spotify user authorisation (run on a machine with a browser).

    python scripts/spotify_authorize.py

Opens Spotify's consent page, captures the redirect, and writes a refresh-token
cache to data/.spotify-user-token-cache. The API server (local or Docker) then
reads that file and auto-refreshes forever — no browser needed again.

Prerequisites:
  - SPOTIPY_CLIENT_ID / SPOTIPY_CLIENT_SECRET set in .env at the repo root.
  - The redirect URI (default http://127.0.0.1:8888/callback, or
    SPOTIFY_REDIRECT_URI) registered in the Spotify dashboard, exactly.

To use the token elsewhere (e.g. Docker), copy/mount the cache file — it's
gitignored, so it is never committed.
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
# Make the `api` / `resources` packages importable so we reuse one source of
# truth for the scopes, redirect URI, and cache path.
sys.path.insert(0, str(ROOT / "functions"))
load_dotenv(ROOT / ".env")

import spotipy  # noqa: E402
from spotipy.cache_handler import CacheFileHandler  # noqa: E402
from spotipy.oauth2 import SpotifyOAuth  # noqa: E402

from api.deps import (  # noqa: E402
    SPOTIFY_USER_SCOPES,
    redirect_uri,
    user_token_cache_path,
)


def main() -> int:
    cache = user_token_cache_path()
    cache.parent.mkdir(parents=True, exist_ok=True)
    auth = SpotifyOAuth(
        scope=SPOTIFY_USER_SCOPES,
        redirect_uri=redirect_uri(),
        open_browser=True,
        cache_handler=CacheFileHandler(cache_path=str(cache)),
    )
    sp = spotipy.Spotify(auth_manager=auth)
    me = sp.me()
    print(f"\n✓ Authorised as {me.get('display_name')} ({me.get('id')})")
    print(f"✓ Token cached at {cache}")
    print("  It's gitignored — copy/mount this file into your other environments.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
