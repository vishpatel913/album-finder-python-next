from .model import Artist
from .repository import AbstractArtistRepository


def get_all_artists(repo: AbstractArtistRepository) -> list[Artist]:
    return repo.list()


def get_artist(artist_id: str, repo: AbstractArtistRepository) -> Artist:
    artist = repo.get_by_id(artist_id)
    if not artist:
        raise ValueError(f"Artist id {artist_id} not found")
    return artist
