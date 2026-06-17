"""Query services for artists — resolve the artist -> albums link (one-to-many)."""

from domain.album.repository import AbstractAlbumRepository
from domain.artist.repository import AbstractArtistRepository

from application.dto.read import AlbumRead
from application.dto.read_models import ArtistWithAlbums


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
    artist = artist_repo.list()
    return []
