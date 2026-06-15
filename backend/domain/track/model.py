# from datetime import datetime
# from typing import Optional
# from sqlmodel import SQLModel, Field, Relationship

# from domain.album.model import Album
# from domain.artist.model import Artist

# class TrackBase(SQLModel):
#     name: str = Field(index=True)
#     # artist_id: int = Field(foreign_key="artist.id")
#     # featuring_artist: Optional[str]
#     # album_id: Optional[int] = Field(foreign_key="album.id")
#     track_number: int
#     total_time: int
#     date_added: datetime
#     play_count: Optional[int]

#     # Relationships
#     # artist: Optional["Artist"] = Relationship(back_populates="tracks")
#     # series: Optional["Album"] = Relationship(back_populates="tracks")

# class Track(TrackBase, table=True):
#     id: int | None = Field(default=None, primary_key=True)

