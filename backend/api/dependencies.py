from domain.album.repository import SqlAlbumRepository
from domain.artist.repository import SqlArtistRepository
from domain.track.repository import SqlTrackRepository
from fastapi import Depends
from sqlmodel import Session

from database.session import get_session


def get_album_repo(session: Session = Depends(get_session)) -> SqlAlbumRepository:
    return SqlAlbumRepository(session)


def get_artist_repo(session: Session = Depends(get_session)) -> SqlArtistRepository:
    return SqlArtistRepository(session)


def get_track_repo(session: Session = Depends(get_session)) -> SqlTrackRepository:
    return SqlTrackRepository(session)
