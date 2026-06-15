# from domain.album.schema import AlbumRead
from sqlmodel import SQLModel

class ArtistCreate(SQLModel):
    id: str
    name: str


class ArtistRead(SQLModel):
    id: str
    name: str
    # albums: list["AlbumRead"]
