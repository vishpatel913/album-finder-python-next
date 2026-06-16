"""Write use cases for albums (commands).

Orchestrate state changes: input *shape* is validated by the schema at the route
boundary; cross-aggregate rules (e.g. "linked artist must exist") live here;
single-aggregate invariants belong on the model; the repo just persists.
"""

# TODO: def update_album(album_id, data, album_repo, artist_repo) -> AlbumRead: ...
