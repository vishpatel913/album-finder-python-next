"""Query services for albums — resolve the album -> artist link (many-to-one)."""

from application.dto.read import ArtistRead
from application.dto.read_models import AlbumDetails
from domain.album.repository import AbstractAlbumRepository
from domain.artist.repository import AbstractArtistRepository
from domain.track.repository import AbstractTrackRepository


def get_album_details(
    album_id: str,
    album_repo: AbstractAlbumRepository,
    artist_repo: AbstractArtistRepository,
    track_repo: AbstractTrackRepository,
) -> AlbumDetails:
    """One album with its artist resolved. Raises ValueError if not found."""
    album = album_repo.get_by_id(album_id)
    if not album:
        raise ValueError(f"Album id {album_id} not found")

    data = album.model_dump()

    if album.artist_id:
        artist = artist_repo.get_by_id(album.artist_id)
        data["artist"] = artist.model_dump() if artist else None
    else:
        data["artist"] = None

    tracks = track_repo.list_by_album(album.id)
    data["tracks"] = [track.model_dump() for track in tracks]

    return AlbumDetails.model_validate(data)


def list_albums_details(
    album_repo: AbstractAlbumRepository,
    artist_repo: AbstractArtistRepository,
) -> list[AlbumDetails]:
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

    results: list[AlbumDetails] = []
    for album in albums:
        item = AlbumDetails.model_validate(album, from_attributes=True)
        artist = by_id.get(album.artist_id) if album.artist_id else None
        item.artist = (
            ArtistRead.model_validate(artist, from_attributes=True) if artist else None
        )
        results.append(item)
    return results
