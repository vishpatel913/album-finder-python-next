# from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

# if TYPE_CHECKING:
    # from domain.artist.model import Artist
    # from domain.track.model import Track



class AlbumBase(SQLModel):
    name: str = Field(index=True)
    artist_id: str | None = Field(default=None, foreign_key="artist.id")
    genre: str
    year: int
    date_added: str | None = None
    is_compilation: bool

    # Relationships
    # artist: "Artist" = Relationship(back_populates="albums")
    # # tracks: list["Track"] = Relationship(back_populates="album")

    # def total_tracks(self) -> int:
    #     return self.tracks.__len__


class Album(AlbumBase, table=True):
    id: str | None = Field(default=None, primary_key=True)
