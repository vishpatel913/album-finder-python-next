# from domain.artist.schema import ArtistRead
from sqlmodel import SQLModel

class AlbumCreate(SQLModel):
    id: str
    name: str
    artist_id: int
    genre: str
    year: int


class AlbumRead(SQLModel):
    id: str
    name: str
    # artist: "ArtistRead"
    genre: str
    year: int
