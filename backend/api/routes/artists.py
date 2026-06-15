from domain.artist.schema import ArtistRead
from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_artist_repo
from domain.artist import service

router = APIRouter(prefix="/artist", tags=["artist"])


@router.get("/", response_model=list[ArtistRead])
def list_artist(repo=Depends(get_artist_repo)):
    return service.get_all_artists(repo)


@router.get("/{artist_id}", response_model=ArtistRead)
def get_artist(artist_id: int, repo=Depends(get_artist_repo)):
    try:
        return service.get_artist(artist_id, repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
