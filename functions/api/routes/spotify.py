"""Spotify enrichment endpoints.

The FE calls these to populate artist images + Spotify "vibe" tags into
the cache. Each call may hit Spotify if the entry isn't cached; misses
are recorded so we don't re-search next time.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_album_resolver, get_parsed_library, get_resolver
from api.schemas import EnrichRequest
from resources.music_library import enrichable_albums, enrichable_artist_names

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
