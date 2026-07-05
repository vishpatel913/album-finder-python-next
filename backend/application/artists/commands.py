"""Write use cases for artists (commands)"""

from application.dto.read import ArtistRead
from application.ports.enrichment import MusicEnrichmentPort
from domain.artist.repository import AbstractArtistRepository


def enrich_artist(
    artist_id: str,
    enrichment: MusicEnrichmentPort,
    artist_repo: AbstractArtistRepository,
) -> ArtistRead:
    artist = artist_repo.get_by_id(artist_id)
    if not artist:
        raise ValueError(f"artist id {artist_id} not found")

    search_query = "artist:" + artist.name

    enrichment_data = enrichment.search(search_query, "artist")
    results = (
        enrichment_data.items.artists
        if enrichment_data and enrichment_data.items and enrichment_data.items.artists
        else []
    )
    top_result = results[0]

    enriched_fields = {"spotify_id": top_result.id, "image_url": top_result.image_url}
    if not artist:
        raise ValueError(f"artist enriched for {artist_id} failed")

    updated = artist_repo.update(artist_id, enriched_fields)

    if not updated:
        raise ValueError(f"artist could not update for {artist_id}")

    return ArtistRead(
        id=updated.id,
        name=updated.name,
        image_url=updated.image_url,
        spotify_id=updated.spotify_id,
    )
