"""Cross-aggregate read models (the CQRS read side).

These live here, not in either domain package, so neither domain has to import
the other. They compose the per-aggregate ``*Read`` schemas into the shapes the
API returns. Domain/write models keep ID references only (e.g. Album.artist_id);
the resolved object graph exists only on the read side.

Expose these per endpoint as a coarse equivalent of GraphQL field selection:
return ``AlbumRead`` when you don't need the relation, ``AlbumWithArtist`` when
you do.
"""

from domain.album.schema import AlbumRead
from domain.artist.schema import ArtistRead


class AlbumWithArtist(AlbumRead):
    """An album with its (many-to-one) artist resolved."""

    artist: ArtistRead | None = None


class ArtistWithAlbums(ArtistRead):
    """An artist with its (one-to-many) albums resolved."""

    albums: list[AlbumRead] = []
