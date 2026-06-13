from abc import ABC, abstractmethod

from sqlmodel import Session, select

from .model import Album


class AbstractAlbumRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Album | None: ...

    @abstractmethod
    def list(self) -> list[Album]: ...

    @abstractmethod
    def update(self, id: int, fields: dict) -> Album | None: ...


class SqlAlbumRepository(AbstractAlbumRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: int) -> Album | None:
        return self.session.get(Album, id)

    def list(self) -> list[Album]:
        return self.session.exec(select(Album)).all()

    def update(self, id: int, fields: dict) -> Album | None:
        album = self.session.get(Album, id)
        if album is None:
            return None
        for key, value in fields.items():
            setattr(album, key, value)
        self.session.add(album)
        self.session.commit()
        self.session.refresh(album)
        return album
