"""Cross-aggregate read models (the CQRS read side)."""

from application.dto.read import AlbumRead, ArtistRead, TrackRead


class AlbumDetails(AlbumRead):
    """An album with its relational fields resolved."""

    artist: ArtistRead | None = None
    tracks: list[TrackRead] = []


class ArtistDetails(ArtistRead):
    """An album with its (one-to-many) albums resolved."""

    albums: list[AlbumRead] = []
