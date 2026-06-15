from domain.album.schema import AlbumRead
from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_album_repo
from domain.album import service

router = APIRouter(prefix="/album", tags=["album"])


@router.get("/", response_model=list[AlbumRead])
def list_album(repo=Depends(get_album_repo)):
    return service.get_all_albums(repo)


@router.get("/{book_id}", response_model=AlbumRead)
def get_album(book_id: int, repo=Depends(get_album_repo)):
    try:
        return service.get_album(book_id, repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
