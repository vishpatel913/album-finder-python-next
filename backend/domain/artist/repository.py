from abc import ABC, abstractmethod
from collections.abc import Iterable

from sqlmodel import Session, col, select

from .model import Artist


class AbstractArtistRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> Artist | None: ...

    @abstractmethod
    def get_by_ids(self, ids: Iterable[str]) -> list[Artist]: ...

    @abstractmethod
    def list(self) -> list[Artist]: ...

    @abstractmethod
    def create(self, entity: Artist) -> Artist: ...

    @abstractmethod
    def update(self, id: str, fields: dict) -> Artist | None: ...

    @abstractmethod
    def upsert(self, entity: Artist) -> None: ...

    @abstractmethod
    def delete(self, id: str) -> bool: ...


class SqlArtistRepository(AbstractArtistRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: str) -> Artist | None:
        return self.session.get(Artist, id)

    def get_by_ids(self, ids: Iterable[str]) -> list[Artist]:
        return list(
            self.session.exec(select(Artist).where(col(Artist.id).in_(ids))).all()
        )

    def list(self) -> list[Artist]:
        return list(self.session.exec(select(Artist)).all())

    def create(self, entity: Artist) -> Artist:
        """Persist a new artist and return the stored row."""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def update(self, id: str, fields: dict) -> Artist | None:
        artist = self.session.get(Artist, id)
        if artist is None:
            return None
        for key, value in fields.items():
            setattr(artist, key, value)
        self.session.add(artist)
        self.session.commit()
        self.session.refresh(artist)
        return artist

    def upsert(self, entity: Artist) -> None:
        """Stage an insert or in-place update by id. Caller owns the transaction."""
        existing = self.session.get(Artist, entity.id)
        if existing is None:
            self.session.add(entity)
        else:
            for key, value in entity.model_dump(exclude={"id"}).items():
                setattr(existing, key, value)
            self.session.add(existing)

    def delete(self, id: str) -> bool:
        """Delete by id. Returns True if a row was removed, False if not found."""
        artist = self.session.get(Artist, id)
        if artist is None:
            return False
        self.session.delete(artist)
        self.session.commit()
        return True
