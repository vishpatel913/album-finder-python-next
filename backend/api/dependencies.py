from fastapi import Depends
from sqlmodel import Session

from application.ports.enrichment import MusicEnrichmentPort
from domain.album.repository import SqlAlbumRepository
from domain.artist.repository import SqlArtistRepository
from domain.track.repository import SqlTrackRepository
from infrastructure.database.session import get_session
from infrastructure.spotify.client import SpotifyEnrichmentClient


def get_album_repo(session: Session = Depends(get_session)) -> SqlAlbumRepository:
    return SqlAlbumRepository(session)


def get_artist_repo(session: Session = Depends(get_session)) -> SqlArtistRepository:
    return SqlArtistRepository(session)


def get_track_repo(session: Session = Depends(get_session)) -> SqlTrackRepository:
    return SqlTrackRepository(session)


def get_enrichment_service() -> MusicEnrichmentPort:
    return SpotifyEnrichmentClient()
