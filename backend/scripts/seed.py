import os
from pathlib import Path
from domain.track.model import Track
from domain.track.schema import TrackCreate
from domain.artist.model import Artist
from domain.artist.schema import ArtistCreate
from sqlmodel import Session
from domain.album.model import Album
from database.session import session_scope
from domain.album.schema import AlbumCreate
from libs.music_library.parser import extract_albums, extract_artists, parse_library

# Point this at any iTunes-style XML dump. Override with the SEED_FIXTURE env
# var (relative paths resolve against the working dir); otherwise defaults to
# backend/fixtures/sample_library.xml. In dev the fixtures dir is bind-mounted,
# so you can drop a new dump in and the watcher re-runs the seed.
DEFAULT_FIXTURE = (
    Path(__file__).resolve().parent.parent / "fixtures" / "sample_library.xml"
)
FIXTURE = Path(os.getenv("SEED_FIXTURE", DEFAULT_FIXTURE))

def upsert_artist(session: Session, parsed: ArtistCreate) -> None:
    existing = session.get(Artist, parsed.id)
    if existing is None:
        session.add(Artist.model_validate(parsed))
    else:
        for key, value in parsed.model_dump(exclude_unset=True).items():
            setattr(existing, key, value)
        session.add(existing)

def upsert_album(session: Session, parsed: AlbumCreate) -> None:
    existing = session.get(Album, parsed.id)
    if existing is None:
        session.add(Album.model_validate(parsed))
    else:
        for key, value in parsed.model_dump(exclude_unset=True).items():
            setattr(existing, key, value)
        session.add(existing)

def upsert_track(session: Session, parsed: TrackCreate) -> None:
    existing = session.get(Track, parsed.id)
    if existing is None:
        session.add(Track.model_validate(parsed))
    else:
        for key, value in parsed.model_dump(exclude_unset=True).items():
            setattr(existing, key, value)
        session.add(existing)



def seed():
    parsed_tracks = parse_library(FIXTURE)
    print(f"parsed {len(parsed_tracks)} tracks from {FIXTURE}")

    with session_scope() as session:
        for entry in extract_artists(parsed_tracks):
            upsert_artist(session, ArtistCreate.from_library(entry))
        session.flush()

        for entry in extract_albums(parsed_tracks):
            upsert_album(session, AlbumCreate.from_library(entry))
        
        for entry in parsed_tracks:
            upsert_track(session, TrackCreate.from_library(entry))

        session.commit()
        print("Seed complete")


if __name__ == "__main__":
    seed()
    print("Tables seeded / updated with library data")
