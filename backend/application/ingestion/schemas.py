"""Ingestion input DTOs + adapters (anti-corruption layer).

Each ``*Create`` maps a neutral parser dict (from ``libs.music_library``) into a
domain-shaped create model via ``from_library``. These are ingestion-specific
(tied to the Music.app library source), so they live with the seed use case
rather than in the general ``application/dto`` contracts.
"""

from datetime import datetime

from sqlmodel import SQLModel

from utils.slug import slugify


class ArtistCreate(SQLModel):
    id: str
    name: str

    @classmethod
    def from_library(cls, artist: dict) -> ArtistCreate:
        """Adapter: neutral parser artist dict -> domain create model."""
        name = artist["album_artist"]
        return cls(id=slugify(name), name=name)


class AlbumCreate(SQLModel):
    id: str
    name: str
    artist_id: str | None = None
    genre: str | None = None
    year: int | None = None
    date_added: str
    is_compilation: bool

    @classmethod
    def from_library(cls, album: dict) -> AlbumCreate:
        """Adapter: neutral parser album dict -> domain create model."""
        artist = album["album_artist"]
        return cls(
            id=slugify(album["album"], artist),
            name=album["album"],
            artist_id=slugify(artist) if artist else None,
            genre=album["genre"] if album["genre"] else None,
            year=album["year"] if album["year"] else None,
            date_added=album["date_added"],
            is_compilation=album["compilation"],
        )


class TrackCreate(SQLModel):
    id: str
    name: str
    artist: str
    album_id: str
    disc_number: int | None = None
    track_number: int | None = None
    track_length: int | None = None
    date_added: datetime
    play_count: int | None = None

    @classmethod
    def from_library(cls, track: dict) -> TrackCreate:
        """Adapter: neutral parser track dict -> domain create model."""
        return cls(
            id=track["id"],
            name=track["name"],
            artist=track["artist"],
            album_id=slugify(track["album"], track["album_artist"]),
            track_number=track["track_number"] if track["track_number"] else None,
            track_length=track["track_length"] if track["track_length"] else None,
            disc_number=track["disc_number"] if track["disc_number"] else None,
            date_added=track["date_added"],
            play_count=track["play_count"] if track["play_count"] else None,
        )
