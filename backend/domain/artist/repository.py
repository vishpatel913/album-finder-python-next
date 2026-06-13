from abc import ABC, abstractmethod

from sqlmodel import Session, select

from .model import Artist


class AbstractArtistRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Artist | None: ...

    @abstractmethod
    def list(self) -> list[Artist]: ...

    @abstractmethod
    def update(self, id: int, fields: dict) -> Artist | None: ...


class SqlArtistRepository(AbstractArtistRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: int) -> Artist | None:
        return self.session.get(Artist, id)

    def list(self) -> list[Artist]:
        return self.session.exec(select(Artist)).all()

    def update(self, id: int, fields: dict) -> Artist | None:
        artist = self.session.get(Artist, id)
        if artist is None:
            return None
        for key, value in fields.items():
            setattr(artist, key, value)
        self.session.add(artist)
        self.session.commit()
        self.session.refresh(artist)
        return artist
