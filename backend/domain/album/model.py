# from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, SQLModel

# if TYPE_CHECKING:
# from domain.artist.model import Artist
# from domain.track.model import Track


class AlbumBase(SQLModel):
    name: str = Field(index=True)
    artist_id: str = Field(default="unknown", foreign_key="artist.id")
    genre: str | None = None
    year: int | None = None
    date_added: str
    is_compilation: bool
    artwork_url: str | None = None

    spotify_id: str | None = None
    # spotify_url: str | None = None

    # Relationships
    # artist: "Artist" = Relationship(back_populates="albums")
    # # tracks: list["Track"] = Relationship(back_populates="album")

    # def total_tracks(self) -> int:
    #     return self.tracks.__len__


class Album(AlbumBase, table=True):
    id: str = Field(primary_key=True)
