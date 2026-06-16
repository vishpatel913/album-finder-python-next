"""Spotify adapter — implements MusicEnrichmentPort by wrapping the spotipy lib.

Only this module imports spotipy; the rest of the app depends on the port.
Wire it in ``api/dependencies`` (e.g. a ``get_enrichment`` provider) when ready.
"""

from application.ports.enrichment import MusicEnrichmentPort


class SpotifyEnrichment(MusicEnrichmentPort):
    def __init__(self, client_id: str, client_secret: str) -> None:
        # TODO: build a spotipy.Spotify client (client-credentials) here.
        self._client_id = client_id
        self._client_secret = client_secret

    def get_artist(self, spotify_id: str) -> dict | None:
        # TODO: return self._spotify.artist(spotify_id)
        raise NotImplementedError

    def search_artist(self, name: str) -> dict | None:
        # TODO: self._spotify.search(q=name, type="artist") -> best match
        raise NotImplementedError
