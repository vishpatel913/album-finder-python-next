from datetime import datetime

from sqlmodel import Field, SQLModel

# from domain.album.model import Album
# from domain.artist.model import Artist


class TrackBase(SQLModel):
    name: str = Field(index=True)
    artist: str
    featuring_artist: str | None = None
    album_id: str | None = Field(default=None, foreign_key="album.id")
    disc_number: int | None = None
    track_number: int | None = None
    track_length: int | None = None
    date_added: datetime
    play_count: int | None = None

    spotify_id: str | None = None

    # Relationships
    # artist: Optional["Artist"] = Relationship(back_populates="tracks")
    # series: Optional["Album"] = Relationship(back_populates="tracks")


class Track(TrackBase, table=True):
    id: str | None = Field(default=None, primary_key=True)
