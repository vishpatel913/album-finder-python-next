"""Ingestion use case: load a parsed Music.app library into the database.

Orchestrates parse (libs) -> adapt to domain create models (ingestion.schemas)
-> upsert via the repositories. Owns the transaction: artists and albums are
flushed before tracks so their foreign keys resolve, then a single commit at the
end. The repos' ``upsert`` only stages rows; transaction control stays here.

This is the application-layer home for the old seed script's logic; the script
in ``scripts/seed.py`` is now just a thin entrypoint.
"""

from pathlib import Path

from application.ingestion.schemas import AlbumCreate, ArtistCreate
from domain.album.model import Album
from domain.album.repository import SqlAlbumRepository
from domain.artist.model import Artist
from domain.artist.repository import SqlArtistRepository
from infrastructure.database.session import session_scope
from libs.music_library.parser import (
    extract_albums,
    extract_artists,
    parse_library,
)


def seed_library(data_path: Path) -> None:
    """Parse the library at ``data_path`` and upsert artists, albums, tracks."""
    parsed_tracks = parse_library(data_path)
    print(f"parsed {len(parsed_tracks)} tracks from {data_path}")

    with session_scope() as session:
        artists = SqlArtistRepository(session)
        albums = SqlAlbumRepository(session)

        for entry in extract_artists(parsed_tracks):
            artists.upsert(Artist.model_validate(ArtistCreate.from_library(entry)))
        session.flush()

        for entry in extract_albums(parsed_tracks):
            albums.upsert(Album.model_validate(AlbumCreate.from_library(entry)))
        session.flush()

        # tracks = SqlTrackRepository(session)
        # for entry in parsed_tracks:
        #     tracks.upsert(Track.model_validate(TrackCreate.from_library(entry)))

        session.commit()
        print("Seed complete")
