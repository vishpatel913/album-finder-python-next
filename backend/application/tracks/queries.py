"""Read use cases for tracks.

A track references both an artist and an album (many-to-one each), so composed
reads here resolve those links via the artist/album repos — same batched pattern
as albums/queries.py.
"""

# TODO: def get_track_with_relations(track_id, track_repo, artist_repo, album_repo): ...
