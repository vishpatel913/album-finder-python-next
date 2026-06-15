import os
from pathlib import Path

# from database import session
from libs.music_library.parser import extract_albums, extract_artists, parse_library

# Point this at any iTunes-style XML dump. Override with the SEED_FIXTURE env
# var (relative paths resolve against the working dir); otherwise defaults to
# backend/fixtures/sample_library.xml. In dev the fixtures dir is bind-mounted,
# so you can drop a new dump in and the watcher re-runs the seed.
DEFAULT_FIXTURE = (
    Path(__file__).resolve().parent.parent / "fixtures" / "sample_library.xml"
)
FIXTURE = Path(os.getenv("SEED_FIXTURE", DEFAULT_FIXTURE))

# def upsert_book(session: Session, parsed: BookCreate) -> None:
#     existing = session.get(Book, parsed.id)
#     if existing is None:
#         session.add(Book.model_validate(parsed))
#     else:
#         for key, value in parsed.model_dump(exclude_unset=True).items():
#             setattr(existing, key, value)
#         session.add(existing)


def seed():
    parsed_tracks = parse_library(FIXTURE)
    print(f"parsed {len(parsed_tracks)} tracks from {FIXTURE}")

    for entry in extract_albums(parsed_tracks):
        print(entry)
        pass
    
    for entry in extract_artists(parsed_tracks):
        print(entry)
        pass

    # with Session(engine) as session:
    #     for entry in root.findall("entry"):
    #         print(entry)
    #         pass

    #     session.commit()
    #     print("Seed complete")


if __name__ == "__main__":
    seed()
    print("Tables seeded / updated with library data")
