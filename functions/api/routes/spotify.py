"""Spotify enrichment endpoints.

The FE calls these to populate artist images + Spotify "vibe" tags into
the cache. Each call may hit Spotify if the entry isn't cached; misses
are recorded so we don't re-search next time.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from api.deps import (
    get_album_resolver,
    get_parsed_library,
    get_resolver,
    get_spotify_user,
)
from api.schemas import EnrichRequest, LibraryToggleRequest
from resources.music_library import enrichable_albums, enrichable_artist_names

# Spotify's contains endpoints cap IDs per request: 50 for follow checks,
# 20 for saved-album checks. We chunk to stay within these.
_CONTAINS_CHUNK = {"artist": 50, "album": 20}

router = APIRouter(prefix="/api/spotify", tags=["spotify"])


@router.get("/artist/{name}")
def resolve_artist(name: str, resolver=Depends(get_resolver)) -> dict:
    entry = resolver.resolve(name)
    resolver.save()
    if not entry or not entry.get("id"):
        raise HTTPException(status_code=404, detail=f"No Spotify match for {name!r}")
    return entry


@router.post("/enrich")
def enrich(payload: EnrichRequest, resolver=Depends(get_resolver)) -> dict[str, dict | None]:
    results = resolver.resolve_many(payload.names)
    resolver.save()
    return results


@router.post("/enrich-all")
def enrich_all(
    parsed: dict = Depends(get_parsed_library),
    resolver=Depends(get_resolver),
) -> dict:
    """Batch-resolve artists with non-compilation albums into the cache.

    Compilation-only artists (Various-Artists spillover) are skipped — see
    `enrichable_artist_names`. Idempotent: `resolve_many` skips already-cached
    artists, so re-running only fetches new music.
    """
    names = enrichable_artist_names(parsed)
    results = resolver.resolve_many(names)
    resolver.save()
    matched = sum(1 for v in results.values() if v and v.get("id"))
    return {
        "total_artists": len(parsed),
        "enrichable": len(names),
        "skipped_compilation_only": len(parsed) - len(names),
        "matched": matched,
    }


@router.post("/enrich-albums-all")
def enrich_albums_all(
    parsed: dict = Depends(get_parsed_library),
    resolver=Depends(get_album_resolver),
    include_greatest_hits: bool = False,
) -> dict:
    """Batch-resolve real albums (non-compilation, non-greatest-hits) into the
    album cache. Idempotent — already-cached albums are skipped."""
    albums = enrichable_albums(parsed, skip_greatest_hits=not include_greatest_hits)
    pairs = [(a["artist"], a["album"]) for a in albums]
    results = resolver.resolve_many(pairs)
    resolver.save()
    matched = sum(1 for v in results.values() if v and v.get("id"))
    return {"enrichable_albums": len(pairs), "matched": matched}


# --- Write actions: follow artists / save albums on the user's behalf ---
# These need the user-authorised client (get_spotify_user), which 503s with a
# clear message until the one-time consent has been run. See docs.


@router.get("/library/contains")
def library_contains(
    type: Literal["artist", "album"],
    ids: str = Query(..., description="Comma-separated Spotify IDs"),
    sp=Depends(get_spotify_user),
) -> dict[str, bool]:
    """Return {spotify_id: is_followed_or_saved} for the given IDs, so the FE
    can render the correct initial like state. Unknown/empty IDs are dropped."""
    id_list = [i for i in (s.strip() for s in ids.split(",")) if i]
    if not id_list:
        return {}
    chunk = _CONTAINS_CHUNK[type]
    out: dict[str, bool] = {}
    for start in range(0, len(id_list), chunk):
        batch = id_list[start : start + chunk]
        if type == "artist":
            flags = sp.current_user_following_artists(batch)
        else:
            flags = sp.current_user_saved_albums_contains(batch)
        for entity_id, flag in zip(batch, flags):
            out[entity_id] = bool(flag)
    return out


@router.post("/library/toggle")
def library_toggle(payload: LibraryToggleRequest, sp=Depends(get_spotify_user)) -> dict:
    """Follow/unfollow an artist or save/remove an album. `id` is the Spotify
    ID carried on the enriched artist/album. Idempotent on Spotify's side."""
    ids = [payload.id]
    if payload.type == "artist":
        action = sp.user_follow_artists if payload.action == "add" else sp.user_unfollow_artists
    else:
        action = (
            sp.current_user_saved_albums_add
            if payload.action == "add"
            else sp.current_user_saved_albums_delete
        )
    action(ids)
    return {"type": payload.type, "id": payload.id, "action": payload.action, "ok": True}
