from .model import Track
from .repository import AbstractTrackRepository


def get_all_tracks(repo: AbstractTrackRepository) -> list[Track]:
    return repo.list()


def get_track(track_id: str, repo: AbstractTrackRepository) -> Track:
    track = repo.get_by_id(track_id)
    if not track:
        raise ValueError(f"Track id {track_id} not found")
    return track
