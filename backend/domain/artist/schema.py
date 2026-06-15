# from domain.album.schema import AlbumRead
from sqlmodel import SQLModel

from utils.slug import slugify


class ArtistCreate(SQLModel):
    id: str
    name: str

    @classmethod
    def from_library(cls, artist: dict) -> "ArtistCreate":
        """Adapter: neutral parser artist dict -> domain create model."""
        name = artist["album_artist"]
        return cls(id=slugify(name), name=name)


class ArtistRead(SQLModel):
    id: str
    name: str
    # albums: list["AlbumRead"]
