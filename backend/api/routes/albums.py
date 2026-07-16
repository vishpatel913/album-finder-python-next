from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import (
    get_album_repo,
    get_artist_repo,
    get_enrichment_service,
    get_track_repo,
)
from application.albums.commands import enrich_album
from application.albums.queries import (
    get_album_details,
    list_albums_details,
)
from application.dto.read import AlbumRead
from application.dto.read_models import AlbumDetails

router = APIRouter(prefix="/album", tags=["album"])


@router.get("/", response_model=list[AlbumDetails])
def list_albums(
    album_repo=Depends(get_album_repo), artist_repo=Depends(get_artist_repo)
):
    return list_albums_details(album_repo, artist_repo)


@router.get("/{album_id}", response_model=AlbumDetails)
def get_album_by_id(
    album_id: str,
    album_repo=Depends(get_album_repo),
    artist_repo=Depends(get_artist_repo),
    track_repo=Depends(get_track_repo),
):
    try:
        return get_album_details(album_id, album_repo, artist_repo, track_repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/{album_id}/enrich", response_model=AlbumRead | None)
def enrich_album_by_id(
    album_id: str,
    spotify_client=Depends(get_enrichment_service),
    album_repo=Depends(get_album_repo),
    artist_repo=Depends(get_artist_repo),
):
    res = enrich_album(album_id, spotify_client, album_repo, artist_repo)
    if res is None:
        return None

    return res
