"""Output DTOs (read contracts), owned by the application layer.

Moved out of the domain packages: these are boundary concerns, not domain
logic, and the repositories don't depend on them — repos speak the domain
entities in ``domain/<x>/model.py``. The ``*Create`` schemas and their
``from_library`` adapters stay in ``domain/<x>/schema.py`` (tied to ingestion).
"""

from datetime import datetime

from sqlmodel import SQLModel


class AlbumRead(SQLModel):
    id: str
    name: str
    artist_id: str | None = None
    date_added: datetime
    genre: str | None = None
    year: int | None = None
    is_compilation: bool


class ArtistRead(SQLModel):
    id: str
    name: str


class TrackRead(SQLModel):
    id: str
    name: str
    artist: str
    # artist: "ArtistRead"
    # album: "AlbumRead"
    track_number: int | None
    track_length: int
    date_added: datetime
    play_count: int | None
