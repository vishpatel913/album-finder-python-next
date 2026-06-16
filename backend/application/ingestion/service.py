"""Ingestion use case: load a parsed Music.app library into the database.

Orchestrates parse (libs) -> adapt to domain create models (ingestion.schemas)
-> upsert. Owns the transaction: artists and albums are flushed before tracks so
their foreign keys resolve, then a single commit at the end.

This is the application-layer home for the old seed script's logic; the script
in ``scripts/seed.py`` is now just a thin entrypoint.
"""

from pathlib import Path

from sqlmodel import Session

from application.ingestion.schemas import AlbumCreate, ArtistCreate, TrackCreate
from domain.album.model import Album
from domain.artist.model import Artist
from domain.track.model import Track
from infrastructure.database.session import session_scope
from libs.music_library.parser import (
    extract_albums,
    extract_artists,
    parse_library,
)


def upsert_artist(session: Session, parsed: ArtistCreate) -> None:
    existing = session.get(Artist, parsed.id)
    if existing is None:
        session.add(Artist.model_validate(parsed))
    else:
        for key, value in parsed.model_dump(exclude_unset=True).items():
            setattr(existing, key, value)
        session.add(existing)


def upsert_album(session: Session, parsed: AlbumCreate) -> None:
    existing = session.get(Album, parsed.id)
    if existing is None:
        session.add(Album.model_validate(parsed))
    else:
        for key, value in parsed.model_dump(exclude_unset=True).items():
            setattr(existing, key, value)
        session.add(existing)


def upsert_track(session: Session, parsed: TrackCreate) -> None:
    existing = session.get(Track, parsed.id)
    if existing is None:
        session.add(Track.model_validate(parsed))
    else:
        for key, value in parsed.model_dump(exclude_unset=True).items():
            setattr(existing, key, value)
        session.add(existing)


def seed_library(data_path: Path) -> None:
    """Parse the library at ``data_path`` and upsert artists, albums, tracks."""
    parsed_tracks = parse_library(data_path)
    print(f"parsed {len(parsed_tracks)} tracks from {data_path}")

    with session_scope() as session:
        for entry in extract_artists(parsed_tracks):
            upsert_artist(session, ArtistCreate.from_library(entry))
        session.flush()

        for entry in extract_albums(parsed_tracks):
            upsert_album(session, AlbumCreate.from_library(entry))
        session.flush()

        # for entry in parsed_tracks:
        #     upsert_track(session, TrackCreate.from_library(entry))

        session.commit()
        print("Seed complete")
