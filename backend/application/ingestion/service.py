"""Ingestion use case: load a parsed Music.app library into the database.

Orchestrates parse (libs) -> adapt to domain create models (ingestion.schemas)
-> upsert via the repositories. Owns the transaction: artists and albums are
flushed before tracks so their foreign keys resolve, then a single commit at the
end. The repos' ``upsert`` only stages rows; transaction control stays here.

This is the application-layer home for the old seed script's logic; the script
in ``scripts/seed.py`` is now just a thin entrypoint.
"""

from pathlib import Path

from application.ingestion.schemas import AlbumCreate, ArtistCreate, TrackCreate
from domain.album.model import Album
from domain.album.repository import SqlAlbumRepository
from domain.artist.model import Artist
from domain.artist.repository import SqlArtistRepository
from domain.track.model import Track
from domain.track.repository import SqlTrackRepository
from infrastructure.database.session import session_scope
from libs.music_library.parser import MusicLibraryParser


def seed_library(data_path: Path) -> None:
    """Parse the library at ``data_path`` and upsert artists, albums, tracks."""
    parser = MusicLibraryParser(data_path)
    parsed_tracks = parser.get_tracks()
    print(f"parsed {len(parsed_tracks)} tracks from {data_path}")

    with session_scope() as session:
        artists = SqlArtistRepository(session)
        albums = SqlAlbumRepository(session)
        tracks = SqlTrackRepository(session)

        for entry in parser.get_artists():
            artists.upsert(Artist.model_validate(ArtistCreate.from_library(entry)))
        session.flush()

        for entry in parser.get_albums():
            albums.upsert(Album.model_validate(AlbumCreate.from_library(entry)))
        session.flush()

        for entry in parsed_tracks:
            tracks.upsert(Track.model_validate(TrackCreate.from_library(entry)))
        session.flush()

        session.commit()
        print("Seed complete")
