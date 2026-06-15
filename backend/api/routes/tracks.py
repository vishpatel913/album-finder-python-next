from domain.track.schema import TrackRead
from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_track_repo
from domain.track import service

router = APIRouter(prefix="/track", tags=["track"])


@router.get("/", response_model=list[TrackRead])
def list_track(repo=Depends(get_track_repo)):
    return service.get_all_tracks(repo)


@router.get("/{track_id}", response_model=TrackRead)
def get_track(track_id: str, repo=Depends(get_track_repo)):
    try:
        return service.get_track(track_id, repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
