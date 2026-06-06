"""Spotify enrichment endpoints.

The FE calls these to populate artist images + Spotify "vibe" tags into
the cache. Each call may hit Spotify if the entry isn't cached; misses
are recorded so we don't re-search next time.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_parsed_library, get_resolver
from api.schemas import EnrichRequest

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
    """Batch-resolve every parsed artist into the cache.

    Idempotent: `resolve_many` skips artists already cached, so re-running
    only fetches new music. This is the "request Spotify once" entry point.
    """
    names = list(parsed.keys())
    results = resolver.resolve_many(names)
    resolver.save()
    matched = sum(1 for v in results.values() if v and v.get("id"))
    return {"requested": len(names), "matched": matched, "missed": len(names) - matched}
