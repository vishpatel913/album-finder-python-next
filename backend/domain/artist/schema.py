from domain.album.schema import AlbumRead
from sqlmodel import SQLModel

# class ArtistCreate(SQLModel):
#     name: str


class ArtistRead(SQLModel):
    id: int
    name: str
    albums: list["AlbumRead"]
