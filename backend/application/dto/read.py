"""Output DTOs (read contracts), owned by the application layer.

Moved out of the domain packages: these are boundary concerns, not domain
logic, and the repositories don't depend on them — repos speak the domain
entities in ``domain/<x>/model.py``. The ``*Create`` schemas and their
``from_library`` adapters stay in ``domain/<x>/schema.py`` (tied to ingestion).
"""

from sqlmodel import SQLModel


class AlbumRead(SQLModel):
    id: str
    name: str
    artist_id: str | None = None
    date_added: str
    genre: str | None = None
    year: int | None = None
    is_compilation: bool
    artwork_url: str | None = None

    spotify_id: str | None = None
    spotify_url: str | None = None


class ArtistRead(SQLModel):
    id: str
    name: str
    image_url: str | None = None

    spotify_id: str | None = None
    spotify_url: str | None = None


class TrackRead(SQLModel):
    id: str
    name: str
    artist: str
    # album: "AlbumRead"
    disc_number: int | None
    track_number: int | None
    track_length: int
    date_added: str
    play_count: int | None

    spotify_id: str | None = None
