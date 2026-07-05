from typing import Literal

from pydantic import BaseModel

SearchType = Literal["album", "artist", "track", "playlist"]

AlbumType = Literal["album", "single", "compilation"]


class Album(BaseModel):
    id: str | None
    name: str | None
    imageUrl: str | None
    total_tracks: int | None
    release_date: str | None
    type: AlbumType | None
    uri: str | None
    external_url: str | None
    artist_ids: list[str]


class Artist(BaseModel):
    id: str | None
    name: str | None
    imageUrl: str | None
    uri: str | None
    external_url: str | None


class Track(BaseModel):
    id: str
    name: str
    album_id: str
    artist_ids: list[str]
    track_number: int
    disc_number: int | None
    uri: str
    explicit: bool
    external_url: str | None


class SearchResultItems(BaseModel):
    albums: list[Album] | None
    artists: list[Artist] | None
    # tracks: list[Track] | None


class SearchResult(BaseModel):
    type: SearchType
    total: int
    items: SearchResultItems
