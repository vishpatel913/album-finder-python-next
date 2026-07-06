"""Spotify adapter — implements MusicEnrichmentPort by wrapping the spotipy lib.

Only this module imports spotipy; the rest of the app depends on the port.
"""

import logging
from typing import TypeVar

import spotipy
from pydantic import BaseModel
from spotipy.oauth2 import SpotifyClientCredentials

from application.ports.enrichment import MusicEnrichmentPort
from application.ports.enrichment_types import (
    Album,
    Artist,
    SearchResult,
    SearchResultItems,
)
from infrastructure.spotify.error_handling import handle_validation_errors
from infrastructure.types.generated import (
    ArtistObject,
    SimplifiedAlbumObject,
    SimplifiedArtistObject,
)

RawSearchResponse = TypeVar("RawSearchResponse", bound=BaseModel)

SEARCH_LIMIT = 3

logger = logging.getLogger(__name__)


class SpotifyEnrichmentClient(MusicEnrichmentPort):
    def __init__(self) -> None:
        auth_manager = SpotifyClientCredentials()
        try:
            self.spotifyClient = spotipy.Spotify(auth_manager=auth_manager)
        except Exception:
            logger.info("Failed to connect to Spotify")
            raise

        logger.info("Connected to library API client")

    def search(self, query, search_type):
        raw_response = self.spotifyClient.search(
            q=query, limit=10, offset=0, type=search_type
        )
        if raw_response is None:
            return None

        albums = []
        album_results = raw_response.get("albums", {})
        for item in album_results.get("items") or []:
            albums.append(self._to_album(item))

        artists = []
        artist_results = raw_response.get("artists", {})
        for item in artist_results.get("items") or []:
            artists.append(self._to_artist(item))

        result_items = SearchResultItems(albums=albums, artists=artists)
        return SearchResult(type=search_type, total=0, items=result_items)

    def get_album(self, id: str) -> Album | None:
        raw_response = self.spotifyClient.album(album_id=id)
        if raw_response is None:
            return None

        return self._to_album(raw_response)

    def get_artist(self, id: str) -> Artist | None:
        raw_response = self.spotifyClient.artist(artist_id=id)
        if raw_response is None:
            return None

        return self._to_artist(raw_response)

    def get_artist_albums(self, id: str) -> list[Album] | None:
        raw_response = self.spotifyClient.artist_albums(artist_id=id)
        if raw_response is None:
            return None

        albums = []
        for item in raw_response.get("items") or []:
            albums.append(self._to_album(item))

        return albums

    def get_album_tracks(self, id: str) -> None:
        raise NotImplementedError

    @handle_validation_errors
    def _to_album(self, raw_album: SimplifiedAlbumObject) -> Album:
        album = SimplifiedAlbumObject.model_validate(raw_album)
        artists = [
            artist
            for raw in album.artists
            if (artist := self._to_artist(raw)) is not None
        ]

        return Album(
            id=album.id,
            name=album.name,
            image_url=album.images[0].url,
            total_tracks=album.total_tracks,
            release_date=album.release_date,
            type=album.album_type.value,
            uri=album.uri,
            external_url=album.external_urls.spotify,
            artists=artists,
        )

    @handle_validation_errors
    def _to_artist(self, raw_artist: ArtistObject | SimplifiedArtistObject) -> Artist:
        artist = SimplifiedArtistObject.model_validate(raw_artist)

        image_url = None
        if isinstance(raw_artist, ArtistObject):
            images = raw_artist.images if raw_artist.images else []
            image_url = images[0].url if images[0] else None

        return Artist(
            id=artist.id,
            name=artist.name,
            image_url=image_url,
            uri=artist.uri,
            external_url=artist.external_urls.spotify if artist.external_urls else None,
        )
