"""Spotify adapter — implements MusicEnrichmentPort by wrapping the spotipy lib.

Only this module imports spotipy; the rest of the app depends on the port.
Wire it in ``api/dependencies`` (e.g. a ``get_enrichment`` provider) when ready.
"""

from datetime import date
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
from infrastructure.types.generated import (
    ArtistObject,
    PagingArtistObject,
    PagingSimplifiedAlbumObject,
    SimplifiedAlbumObject,
)

RawSearchResponse = TypeVar("RawSearchResponse", bound=BaseModel)

SEARCH_LIMIT = 3


class SpotifyEnrichment(MusicEnrichmentPort):
    def __init__(self) -> None:
        print("Connecting...")

        auth_manager = SpotifyClientCredentials()
        try:
            self.spotifyClient = spotipy.Spotify(auth_manager=auth_manager)
            print("Connected to Spotify")
        except:
            print("Error connecting to Spotify")

        print()

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
        raw_response = self.spotifyClient.album(album_id=id)
        if raw_response is None:
            return None

        albums: list[Album] = []
        for album in raw_response:
            albums.append(self._to_album(album))

        return albums

    # def get_album_tracks(self, id: str) -> list[Track] | None:

    def search(self, query, type):
        raw_response = self.spotifyClient.search(q=query, limit=10, offset=0, type=type)
        if raw_response is None:
            return None

        album_items = []
        if "album" in raw_response:
            album_results: PagingSimplifiedAlbumObject = raw_response["album"]
            for item in album_results.items if album_results.items else []:
                album_items.append(self._to_album(item))

        artist_items = []
        if "artist" in raw_response:
            artist_results: PagingArtistObject = raw_response["artist"]
            for item in artist_results.items if artist_results.items else []:
                artist_items.append(self._to_artist(item))

        items = SearchResultItems(albums=album_items, artists=artist_items)
        return SearchResult(type=type, total=0, items=items)

    def _get_artist_ids(self, raw: dict):
        artists = raw.get("artists") or []
        return [a["id"] for a in artists]

    def _to_album(self, raw_album: SimplifiedAlbumObject):
        return Album(
            id=raw_album.id,
            name=raw_album.name,
            imageUrl=raw_album.images[0].url,
            total_tracks=raw_album.total_tracks,
            release_date=date.fromisoformat(raw_album.release_date),
            type=raw_album.album_type.value,
            uri=raw_album.uri,
            external_url=raw_album.external_urls.spotify,
            artist_ids=[artist.id for artist in raw_album.artists if artist.id]
            if raw_album.artists
            else [],
        )

    def _to_artist(self, raw_artist: ArtistObject):
        return Artist(
            id=raw_artist.id,
            name=raw_artist.name,
            imageUrl=raw_artist.images[0].url if raw_artist.images else None,
            uri=raw_artist.uri,
            external_url=raw_artist.external_urls.spotify
            if raw_artist.external_urls
            else None,
        )
