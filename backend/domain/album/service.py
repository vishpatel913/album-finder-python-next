from .model import Album
from .repository import AbstractAlbumRepository


def get_all_albums(repo: AbstractAlbumRepository) -> list[Album]:
    return repo.list()


def get_album(album_id: int, repo: AbstractAlbumRepository) -> Album:
    album = repo.get_by_id(album_id)
    if not album:
        raise ValueError(f"Album id {album_id} not found")
    return album
