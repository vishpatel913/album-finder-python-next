from datetime import datetime
from typing import Optional
from utils.slug import slugify
from sqlmodel import SQLModel

class TrackCreate(SQLModel):
    id: str
    name: str
    artist: str
    artist_id: str | None = None
    album_id: str
    track_number: int | None = None
    track_length: int
    date_added: datetime
    play_count: int | None = None

    @classmethod
    def from_library(cls, track: dict) -> "TrackCreate":
        """Adapter: neutral parser track dict -> domain create model."""
        return cls(
            id=track["id"],
            name=track["name"],
            artist=track["artist"],
            artist_id=slugify(track["album_artist"]),
            album_id=slugify(track["album"], track["album_artist"]),
            track_number=track['track_number'],
            track_length=track['track_length'],
            date_added=track['date_added'],
            play_count=track['play_count'],
        )

class TrackRead(SQLModel):
    id: str
    name: str
    artist: str
    # artist: "ArtistRead"
    # series: "AlbumRead"
    track_number: Optional[int]
    track_length: int
    date_added: datetime
    play_count: Optional[int]
