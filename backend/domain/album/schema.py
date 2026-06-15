# from domain.artist.schema import ArtistRead
from sqlmodel import SQLModel

from utils.slug import slugify


class AlbumCreate(SQLModel):
    id: str
    name: str
    artist_id: str | None = None
    genre: str
    year: int
    date_added: str | None = None
    is_compilation: bool

    @classmethod
    def from_library(cls, album: dict) -> "AlbumCreate":
        """Adapter: neutral parser album dict -> domain create model."""
        artist = album["album_artist"]
        return cls(
            id=slugify(artist, album["album"]),
            name=album["album"],
            artist_id=slugify(artist) if artist else None,
            genre=album["genre"],
            year=album["year"],
            date_added=album["date_added"],
            is_compilation=album["compilation"],
        )


class AlbumRead(SQLModel):
    id: str
    name: str
    # artist: "ArtistRead"
    genre: str
    year: int
    is_compilation: bool
