from pathlib import Path

from backend.libs.music_library.parser import parse_library

# def upsert_book(session: Session, parsed: BookCreate) -> None:
#     existing = session.get(Book, parsed.id)
#     if existing is None:
#         session.add(Book.model_validate(parsed))
#     else:
#         for key, value in parsed.model_dump(exclude_unset=True).items():
#             setattr(existing, key, value)
#         session.add(existing)


def seed():
    parsed = parse_library(Path("../fixtures/test_library.xml"))
    # create_db_and_tables()
    # tree = ET.parse("../fixtures/test_library.xml")
    # root = tree.getroot()

    print("root", parsed)

    # for entry in root.findall("entry"):
    #     print(entry)
    #     pass

    # with Session(engine) as session:
    #     for entry in root.findall("entry"):
    #         print(entry)
    #         pass

    #     session.commit()
    #     print("Seed complete")


if __name__ == "__main__":
    seed()
