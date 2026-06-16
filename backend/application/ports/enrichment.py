"""Outbound port: music enrichment (e.g. Spotify).

Use cases depend on this interface, never on a concrete client. The adapter
lives in ``infrastructure/spotify`` and is wired in at ``api/dependencies``.
Same ports-and-adapters shape as the repositories.
"""

from abc import ABC, abstractmethod


class MusicEnrichmentPort(ABC):
    @abstractmethod
    def get_artist(self, spotify_id: str) -> dict | None:
        """Fetch one artist's enrichment payload, or None if absent."""
        ...

    @abstractmethod
    def search_artist(self, name: str) -> dict | None:
        """Find the best-matching artist for a name."""
        ...
