from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

# if TYPE_CHECKING:
    # from domain.artist.model import Artist
    # from domain.track.model import Track



class AlbumBase(SQLModel):
    name: str = Field(index=True)
    artist_id: str = Field(foreign_key="artist.id")
    genre: str
    year: int

    # Relationships
    # artist: "Artist" = Relationship(back_populates="albums")
    # # tracks: list["Track"] = Relationship(back_populates="album")

    # def total_tracks(self) -> int:
    #     return self.tracks.__len__


class Album(AlbumBase, table=True):
    id: str | None = Field(default=None, primary_key=True)
