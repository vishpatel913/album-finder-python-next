"""Pydantic response/query models for the FastAPI surface.

Kept thin: these mirror the dict shapes the parser/resolver already
produce. Pydantic v2 handles the JSON conversion so we don't `json.dumps`
by hand.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


SortArtists = Literal["plays_desc", "plays_asc", "name", "added_desc", "added_asc"]
SortTracks = Literal[
    "plays_desc",
    "plays_asc",
    "name",
    "added_desc",
    "added_asc",
    "rating_desc",
    "last_played_desc",
]


class Track(BaseModel):
    name: str
    album: str = ""
    genre: str = ""
    year: int | None = None
    plays: int = 0
    rating: int | None = None
    loved: bool = False
    date_added: str | None = None
    last_played: str | None = None


class Artist(BaseModel):
    name: str
    total_plays: int
    track_count: int
    top_genre: str | None = None
    all_genres: list[str] = []
    year_min: int | None = None
    year_max: int | None = None
    date_added_first: str | None = None
    date_added_last: str | None = None
    avg_rating: float | None = None
    loved_count: int = 0
    # Spotify enrichment — may be null until /api/spotify/enrich populates.
    spotify_id: str | None = None
    display_name: str | None = None
    image_url: str | None = None
    spotify_genres: list[str] = []


class TrackRow(Track):
    artist: str


class Facets(BaseModel):
    genres: list[str]
    year_min: int | None
    year_max: int | None
    total_artists: int
    total_tracks: int


class Health(BaseModel):
    library_path: str
    library_mtime: str | None
    artists_parsed: int
    cache_entries: int


class DuplicateGroup(BaseModel):
    names: list[str]


class EnrichRequest(BaseModel):
    names: list[str] = Field(default_factory=list)
