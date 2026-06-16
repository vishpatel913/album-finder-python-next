"""Query services for albums — resolve the album -> artist link (many-to-one).

Repository methods used:
    AbstractAlbumRepository.get_by_id(id)           (exists)
    AbstractAlbumRepository.list()                  (exists)
    AbstractArtistRepository.get_by_id(id)          (exists)
    AbstractArtistRepository.get_by_ids(ids)        (ADD — batch loader, the
        DataLoader equivalent; expected signature:
            def get_by_ids(self, ids: Iterable[str]) -> list[Artist]
        return whatever exists; missing ids are simply absent)
"""

from domain.album.repository import AbstractAlbumRepository
from domain.artist.repository import AbstractArtistRepository
from domain.artist.schema import ArtistRead

from application.read_models import AlbumWithArtist


def get_album_with_artist(
    album_id: str,
    album_repo: AbstractAlbumRepository,
    artist_repo: AbstractArtistRepository,
) -> AlbumWithArtist:
    """One album with its artist resolved. Raises ValueError if not found."""
    album = album_repo.get_by_id(album_id)
    if not album:
        raise ValueError(f"Album id {album_id} not found")

    result = AlbumWithArtist.model_validate(album, from_attributes=True)
    if album.artist_id:
        # Resolve the link via the *artist* aggregate's repo — no join, no
        # reaching into the album's tables for artist data.
        artist = artist_repo.get_by_id(album.artist_id)
        result.artist = (
            ArtistRead.model_validate(artist, from_attributes=True) if artist else None
        )
    return result


def list_albums_with_artist(
    album_repo: AbstractAlbumRepository,
    artist_repo: AbstractArtistRepository,
) -> list[AlbumWithArtist]:
    """All albums, each with its artist resolved in a single batched lookup."""
    albums = album_repo.list()

    # Collect the distinct artist ids, then resolve them in ONE query rather
    # than one-per-album (avoids N+1).
    artist_ids = {a.artist_id for a in albums if a.artist_id}
    by_id = (
        {artist.id: artist for artist in artist_repo.get_by_ids(artist_ids)}
        if artist_ids
        else {}
    )

    results: list[AlbumWithArtist] = []
    for album in albums:
        item = AlbumWithArtist.model_validate(album, from_attributes=True)
        artist = by_id.get(album.artist_id)
        item.artist = (
            ArtistRead.model_validate(artist, from_attributes=True) if artist else None
        )
        results.append(item)
    return results
