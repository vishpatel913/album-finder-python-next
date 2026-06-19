from sqlmodel import SQLModel

from domain.album.model import Album  # noqa: F401
from domain.artist.model import Artist  # noqa: F401
from domain.track.model import Track  # noqa: F401
from infrastructure.database.session import engine

# from domain.track.model import Track  # noqa: F401


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
    print("Tables created (or already present).")
