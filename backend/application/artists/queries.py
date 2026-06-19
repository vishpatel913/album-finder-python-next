"""Query services for artists — resolve the artist -> albums link (one-to-many)."""

from collections import defaultdict

from application.dto.read import AlbumRead
from application.dto.read_models import ArtistWithAlbums
from domain.album.model import Album
from domain.album.repository import AbstractAlbumRepository
from domain.artist import service
from domain.artist.repository import AbstractArtistRepository


def get_artist_with_albums(
    artist_id: str,
    artist_repo: AbstractArtistRepository,
    album_repo: AbstractAlbumRepository,
) -> ArtistWithAlbums:
    """One artist with its albums resolved. Raises ValueError if not found."""
    artist = artist_repo.get_by_id(artist_id)
    if not artist:
        raise ValueError(f"Artist id {artist_id} not found")

    result = ArtistWithAlbums.model_validate(artist, from_attributes=True)
    # Resolve the link via the *album* aggregate's repo.
    albums = album_repo.list_by_artist(artist_id)
    result.albums = [
        AlbumRead.model_validate(album, from_attributes=True) for album in albums
    ]
    return result


def list_artists_with_albums(
    artist_repo: AbstractArtistRepository,
    album_repo: AbstractAlbumRepository,
) -> list[ArtistWithAlbums]:
    """All artists, each with its albums resolved in a single batched lookup."""
    artists = service.get_all_artists(artist_repo)
    album_by_artist_id: dict[str, list[Album]] = defaultdict(list)
    for album in album_repo.list():
        if album.artist_id is not None:
            album_by_artist_id[album.artist_id].append(album)

    results: list[ArtistWithAlbums] = []
    for artist in artists:
        item = ArtistWithAlbums.model_validate(artist, from_attributes=True)
        albums = album_by_artist_id.get(artist.id, []) if artist.id else []
        item.albums = [
            AlbumRead.model_validate(album, from_attributes=True) for album in albums
        ]
        results.append(item)
    return results
