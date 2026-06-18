from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_album_repo, get_artist_repo
from application.artists.queries import get_artist_with_albums, list_artists_with_albums
from application.dto.read_models import ArtistWithAlbums

router = APIRouter(prefix="/artist", tags=["artist"])


@router.get("/", response_model=list[ArtistWithAlbums])
def list_artist(
    artist_repo=Depends(get_artist_repo),
    album_repo=Depends(get_album_repo)
):
    return list_artists_with_albums(artist_repo, album_repo)


@router.get("/{artist_id}", response_model=ArtistWithAlbums)
def get_artist(
    artist_id: str,
    artist_repo=Depends(get_artist_repo),
    album_repo=Depends(get_album_repo)
):
    try:
        return get_artist_with_albums(artist_id, artist_repo, album_repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
