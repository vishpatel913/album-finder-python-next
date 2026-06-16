from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_album_repo
from application.dto.read import AlbumRead
from domain.album import service

router = APIRouter(prefix="/album", tags=["album"])


@router.get("/", response_model=list[AlbumRead])
def list_album(repo=Depends(get_album_repo)):
    return service.get_all_albums(repo)


@router.get("/{album_id}", response_model=AlbumRead)
def get_album(album_id: int, repo=Depends(get_album_repo)):
    try:
        return service.get_album(album_id, repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
