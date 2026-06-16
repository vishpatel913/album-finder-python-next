"""Cross-aggregate read models (the CQRS read side)."""

from application.dto.read import AlbumRead, ArtistRead


class AlbumWithArtist(AlbumRead):
    """An album with its (many-to-one) artist resolved."""

    artist: ArtistRead | None = None


class ArtistWithAlbums(ArtistRead):
    """An artist with its (one-to-many) albums resolved."""

    albums: list[AlbumRead] = []
