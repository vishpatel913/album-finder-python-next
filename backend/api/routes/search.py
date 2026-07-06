from fastapi import APIRouter, Depends

from api.dependencies import get_enrichment_service
from application.ports.enrichment import MusicEnrichmentPort
from application.ports.enrichment_types import Album, Artist, Track

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/album", response_model=list[Album])
def search_albums(
    q: str, spotify_client: MusicEnrichmentPort = Depends(get_enrichment_service)
):
    res = spotify_client.search(q, "album")
    if res is None or res.items.albums is None:
        return []

    return res.items.albums


@router.get("/album/{album_id}", response_model=Album)
def get_album(
    album_id: str, spotify_client: MusicEnrichmentPort = Depends(get_enrichment_service)
):
    res = spotify_client.get_album(album_id)
    if res is None:
        return []

    return res


@router.get("/album/{album_id}/tracks", response_model=list[Track])
def get_album_tracks(
    album_id: str, spotify_client: MusicEnrichmentPort = Depends(get_enrichment_service)
):
    res = spotify_client.get_album_tracks(album_id)
    if res is None:
        return []

    return res


@router.get("/artist", response_model=list[Artist])
def search_artists(
    q: str, spotify_client: MusicEnrichmentPort = Depends(get_enrichment_service)
):
    res = spotify_client.search(q, "artist")
    if res is None or res.items.artists is None:
        return []

    return res.items.artists


@router.get("/artist/{artist_id}", response_model=Artist)
def get_artist(
    artist_id: str,
    spotify_client: MusicEnrichmentPort = Depends(get_enrichment_service),
):
    res = spotify_client.get_artist(artist_id)
    if res is None:
        return []

    return res


@router.get("/artist/{artist_id}/albums", response_model=list[Album])
def get_artist_albums(
    artist_id: str,
    spotify_client: MusicEnrichmentPort = Depends(get_enrichment_service),
):
    res = spotify_client.get_artist_albums(artist_id)
    if res is None:
        return []

    return res
