"""Cross-aggregate read models (the CQRS read side)."""

import statistics

from pydantic import computed_field

from application.dto.read import AlbumRead, ArtistRead, TrackRead


class AlbumDetails(AlbumRead):
    """An album with its relational fields resolved."""

    artist: ArtistRead | None = None
    tracks: list[TrackRead] = []

    @computed_field
    @property
    def average_play_count(self) -> int | None:
        valid_counts = [
            track.play_count for track in self.tracks if track.play_count is not None
        ]
        if not valid_counts:
            return 0

        return round(statistics.mean(valid_counts))


class ArtistDetails(ArtistRead):
    """An album with its (one-to-many) albums resolved."""

    albums: list[AlbumRead] = []
