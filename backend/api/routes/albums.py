from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_album_repo, get_artist_repo
from application.albums.queries import get_album_with_artist, list_albums_with_artist
from application.dto.read_models import AlbumWithArtist

router = APIRouter(prefix="/album", tags=["album"])


@router.get("/", response_model=list[AlbumWithArtist])
def list_album(
    album_repo=Depends(get_album_repo),
    artist_repo=Depends(get_artist_repo)
):
    return list_albums_with_artist(album_repo, artist_repo)


@router.get("/{album_id}", response_model=AlbumWithArtist)
def get_album(
    album_id: str, 
    album_repo=Depends(get_album_repo),
    artist_repo=Depends(get_artist_repo)
):
    try:
        return get_album_with_artist(album_id, album_repo, artist_repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
