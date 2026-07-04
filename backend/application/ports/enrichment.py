"""Outbound port: music enrichment (e.g. Spotify).

Use cases depend on this interface, never on a concrete client. The adapter
lives in ``infrastructure/spotify`` and is wired in at ``api/dependencies``.
Same ports-and-adapters shape as the repositories.
"""

from abc import ABC, abstractmethod

from enrichment_types import Album, Artist, SearchResult, SearchType, Track

search_types = ["album", "artist", "track"]


class MusicEnrichmentPort(ABC):
    @abstractmethod
    def search(self, query: str, type: SearchType) -> SearchResult | None:
        """Find the best-matching item for a name."""
        ...

    # by spotify id
    @abstractmethod
    def get_album(self, id: str) -> Album | None:
        """Fetch one album's enrichment payload, or None if absent."""
        ...

    @abstractmethod
    def get_album_tracks(self, id: str) -> list[Track] | None:
        """Fetch one album's enrichment payload, or None if absent."""
        ...

    @abstractmethod
    def get_artist(self, id: str) -> Artist | None:
        """Fetch one artist's enrichment payload, or None if absent."""
        ...

    @abstractmethod
    def get_artist_albums(self, id: str) -> list[Album] | None:
        """Fetch one artist's enrichment payload, or None if absent."""
        ...
