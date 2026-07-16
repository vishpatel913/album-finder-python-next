"""Write use cases for albums (commands).

Orchestrate state changes: input *shape* is validated by the schema at the route
boundary; cross-aggregate rules (e.g. "linked artist must exist") live here;
single-aggregate invariants belong on the model; the repo just persists.
"""

from application.dto.read import AlbumRead
from application.ports.enrichment import MusicEnrichmentPort
from domain.album.repository import AbstractAlbumRepository
from domain.artist.repository import AbstractArtistRepository


def enrich_album(
    album_id: str,
    enrichment: MusicEnrichmentPort,
    album_repo: AbstractAlbumRepository,
    artist_repo: AbstractArtistRepository,
) -> AlbumRead:
    album = album_repo.get_by_id(album_id)
    if not album:
        raise ValueError(f"album id {album_id} not found")

    search_query = "album:" + album.name

    if album.artist_id:
        artist = artist_repo.get_by_id(album.artist_id)
        if artist:
            artist_query = "artist:" + artist.name
            search_query += f" {artist_query}"

    enrichment_data = enrichment.search(search_query, "album")
    results = (
        enrichment_data.items.albums
        if enrichment_data and enrichment_data.items and enrichment_data.items.albums
        else []
    )
    top_result = results[0]

    enriched_fields = {
        "spotify_id": top_result.id,
        "artwork_url": top_result.image_url,
        "spotify_url": top_result.external_url,
    }
    if not album:
        raise ValueError(f"album enriched for {album_id} failed")

    updated = album_repo.update(album_id, enriched_fields)

    if not updated:
        raise ValueError(f"album could not update for {album_id}")

    return AlbumRead(
        id=updated.id,
        name=updated.name,
        artist_id=updated.artist_id,
        date_added=updated.date_added,
        genre=updated.genre,
        year=updated.year,
        is_compilation=updated.is_compilation,
        artwork_url=updated.artwork_url,
        spotify_id=updated.spotify_id,
        spotify_url=updated.spotify_url,
    )
