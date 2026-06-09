"""Read endpoints over the parsed Music.app library.

The parser returns a `{album_artist: rollup_dict}`; these endpoints
flatten/filter/sort that into JSON for the FE. Filtering is done in
Python rather than at parse time so the in-memory cache stays a single
source of truth.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from api.deps import get_album_resolver, get_parsed_library, get_resolver
from api.schemas import (
    Album,
    Artist,
    DuplicateGroup,
    Facets,
    SortAlbums,
    SortArtists,
    SortTracks,
    TrackRow,
)
from resources.music_library import albums_from_parsed, find_near_duplicate_artists

router = APIRouter(prefix="/api/library", tags=["library"])


def _matches_substring(haystack: str, needle: str | None) -> bool:
    if not needle:
        return True
    return needle.casefold() in (haystack or "").casefold()


@router.get("/artists", response_model=list[Artist])
def list_artists(
    parsed: dict = Depends(get_parsed_library),
    resolver=Depends(get_resolver),
    limit: int = Query(50, ge=1, le=500),
    min_plays: int = Query(0, ge=0),
    q: str | None = None,
    genre: str | None = None,
    vibe: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    added_after: str | None = None,
    sort: SortArtists = "plays_desc",
) -> list[Artist]:
    rows: list[Artist] = []
    for name, rollup in parsed.items():
        if rollup["total_plays"] < min_plays:
            continue
        if not _matches_substring(name, q):
            continue
        if genre and (rollup.get("top_genre") or "").casefold() != genre.casefold():
            # Allow match against any of the artist's genres, not just top.
            if not any(g.casefold() == genre.casefold() for g in rollup.get("all_genres", [])):
                continue
        if year_from is not None and (rollup.get("year_max") or 0) < year_from:
            continue
        if year_to is not None and (rollup.get("year_min") or 9999) > year_to:
            continue
        if added_after and (rollup.get("date_added_last") or "") < added_after:
            continue

        cached = resolver.get_cached(name) or {}
        spotify_genres = cached.get("genres", [])
        if vibe and not any(vibe.casefold() in g.casefold() for g in spotify_genres):
            continue

        rows.append(Artist(
            name=name,
            total_plays=rollup["total_plays"],
            track_count=rollup["track_count"],
            top_genre=rollup.get("top_genre"),
            all_genres=rollup.get("all_genres", []),
            year_min=rollup.get("year_min"),
            year_max=rollup.get("year_max"),
            date_added_first=rollup.get("date_added_first"),
            date_added_last=rollup.get("date_added_last"),
            avg_rating=rollup.get("avg_rating"),
            loved_count=rollup.get("loved_count", 0),
            spotify_id=cached.get("id"),
            display_name=cached.get("display_name"),
            image_url=cached.get("image_url"),
            spotify_genres=spotify_genres,
            spotify_url=cached.get("spotify_url"),
            spotify_uri=cached.get("uri"),
            popularity=cached.get("popularity"),
            followers=cached.get("followers"),
        ))

    rows = _sort_artists(rows, sort)
    return rows[:limit]


def _sort_artists(rows: list[Artist], sort: SortArtists) -> list[Artist]:
    if sort == "plays_desc":
        return sorted(rows, key=lambda a: a.total_plays, reverse=True)
    if sort == "plays_asc":
        return sorted(rows, key=lambda a: a.total_plays)
    if sort == "name":
        return sorted(rows, key=lambda a: a.name.casefold())
    if sort == "added_desc":
        return sorted(rows, key=lambda a: a.date_added_last or "", reverse=True)
    if sort == "added_asc":
        return sorted(rows, key=lambda a: a.date_added_first or "")
    return rows


@router.get("/albums", response_model=list[Album])
def list_albums(
    parsed: dict = Depends(get_parsed_library),
    album_resolver=Depends(get_album_resolver),
    limit: int = Query(100, ge=1, le=500),
    min_plays: int = Query(0, ge=0),
    q: str | None = None,
    artist: str | None = None,
    genre: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    added_after: str | None = None,
    include_greatest_hits: bool = False,
    sort: SortAlbums = "plays_desc",
) -> list[Album]:
    rows: list[Album] = []
    for a in albums_from_parsed(parsed):
        # Always drop compilations (the "Top 40" Various-Artists albums);
        # greatest-hits/collections are hidden unless explicitly requested.
        if a["compilation"]:
            continue
        if a["is_greatest_hits"] and not include_greatest_hits:
            continue
        if a["total_plays"] < min_plays:
            continue
        if not _matches_substring(a["album"], q):
            continue
        if artist and a["artist"].casefold() != artist.casefold():
            continue
        if genre and not any(g.casefold() == genre.casefold() for g in a["all_genres"]):
            continue
        if year_from is not None and (a["year"] or 0) < year_from:
            continue
        if year_to is not None and (a["year"] or 9999) > year_to:
            continue
        if added_after and (a["date_added_last"] or "") < added_after:
            continue

        cached = album_resolver.get_cached(a["artist"], a["album"]) or {}
        rows.append(Album(
            **a,
            spotify_id=cached.get("id"),
            image_url=cached.get("image_url"),
            spotify_url=cached.get("spotify_url"),
            spotify_uri=cached.get("uri"),
            release_date=cached.get("release_date"),
            total_tracks=cached.get("total_tracks"),
        ))

    rows = _sort_albums(rows, sort)
    return rows[:limit]


def _sort_albums(rows: list[Album], sort: SortAlbums) -> list[Album]:
    if sort == "plays_desc":
        return sorted(rows, key=lambda a: a.total_plays, reverse=True)
    if sort == "plays_asc":
        return sorted(rows, key=lambda a: a.total_plays)
    if sort == "name":
        return sorted(rows, key=lambda a: a.album.casefold())
    if sort == "added_desc":
        return sorted(rows, key=lambda a: a.date_added_last or "", reverse=True)
    if sort == "added_asc":
        return sorted(rows, key=lambda a: a.date_added_first or "")
    if sort == "year_desc":
        return sorted(rows, key=lambda a: a.year or 0, reverse=True)
    if sort == "year_asc":
        return sorted(rows, key=lambda a: a.year or 9999)
    return rows


@router.get("/tracks", response_model=list[TrackRow])
def list_tracks(
    parsed: dict = Depends(get_parsed_library),
    limit: int = Query(100, ge=1, le=1000),
    min_plays: int = Query(0, ge=0),
    artist: str | None = None,
    q: str | None = None,
    genre: str | None = None,
    year: int | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    added_after: str | None = None,
    min_rating: int | None = Query(None, ge=0, le=100),
    loved: bool | None = None,
    sort: SortTracks = "plays_desc",
) -> list[TrackRow]:
    rows: list[TrackRow] = []
    for name, rollup in parsed.items():
        if artist and name.casefold() != artist.casefold():
            continue
        for track in rollup["tracks"]:
            if track["plays"] < min_plays:
                continue
            if not _matches_substring(track["name"], q):
                continue
            if genre and (track.get("genre") or "").casefold() != genre.casefold():
                continue
            if year is not None and track.get("year") != year:
                continue
            if year_from is not None and (track.get("year") or 0) < year_from:
                continue
            if year_to is not None and (track.get("year") or 9999) > year_to:
                continue
            if added_after and (track.get("date_added") or "") < added_after:
                continue
            if min_rating is not None and (track.get("rating") or 0) < min_rating:
                continue
            if loved is not None and bool(track.get("loved")) != loved:
                continue

            rows.append(TrackRow(artist=name, **track))

    rows = _sort_tracks(rows, sort)
    return rows[:limit]


def _sort_tracks(rows: list[TrackRow], sort: SortTracks) -> list[TrackRow]:
    if sort == "plays_desc":
        return sorted(rows, key=lambda t: t.plays, reverse=True)
    if sort == "plays_asc":
        return sorted(rows, key=lambda t: t.plays)
    if sort == "name":
        return sorted(rows, key=lambda t: t.name.casefold())
    if sort == "added_desc":
        return sorted(rows, key=lambda t: t.date_added or "", reverse=True)
    if sort == "added_asc":
        return sorted(rows, key=lambda t: t.date_added or "")
    if sort == "rating_desc":
        return sorted(rows, key=lambda t: t.rating or 0, reverse=True)
    if sort == "last_played_desc":
        return sorted(rows, key=lambda t: t.last_played or "", reverse=True)
    return rows


@router.get("/facets", response_model=Facets)
def get_facets(parsed: dict = Depends(get_parsed_library)) -> Facets:
    genres: set[str] = set()
    years: list[int] = []
    track_total = 0
    for rollup in parsed.values():
        for g in rollup.get("all_genres", []):
            if g:
                genres.add(g)
        if rollup.get("year_min"):
            years.append(rollup["year_min"])
        if rollup.get("year_max"):
            years.append(rollup["year_max"])
        track_total += rollup["track_count"]

    return Facets(
        genres=sorted(genres),
        year_min=min(years) if years else None,
        year_max=max(years) if years else None,
        total_artists=len(parsed),
        total_tracks=track_total,
    )


@router.get("/duplicates", response_model=list[DuplicateGroup])
def get_duplicates(parsed: dict = Depends(get_parsed_library)) -> list[DuplicateGroup]:
    groups = find_near_duplicate_artists(parsed.keys())
    return [DuplicateGroup(names=g) for g in groups]


@router.post("/refresh")
def refresh_library() -> dict:
    parsed = get_parsed_library(force=True)
    return {"artists": len(parsed)}
