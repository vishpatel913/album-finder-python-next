from abc import ABC, abstractmethod

from sqlmodel import Session, col, select

from .model import Album


class AbstractAlbumRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> Album | None: ...

    @abstractmethod
    def list(self) -> list[Album]: ...

    @abstractmethod
    def list_by_artist(self, artist_id: str) -> list[Album]: ...

    @abstractmethod
    def create(self, entity: Album) -> Album: ...

    @abstractmethod
    def update(self, id: str, fields: dict) -> Album | None: ...

    @abstractmethod
    def upsert(self, entity: Album) -> Album: ...

    @abstractmethod
    def delete(self, id: str) -> bool: ...


class SqlAlbumRepository(AbstractAlbumRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: str) -> Album | None:
        return self.session.get(Album, id)

    def list(self) -> list[Album]:
        return list(self.session.exec(select(Album)).all())

    def list_by_artist(self, artist_id: str) -> list[Album]:
        return list(
            self.session.exec(
                select(Album).where(col(Album.artist_id) == artist_id)
            ).all()
        )

    def create(self, entity: Album) -> Album:
        """Persist a new album and return the stored row."""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def update(self, id: str, fields: dict) -> Album | None:
        album = self.session.get(Album, id)
        if album is None:
            return None
        for key, value in fields.items():
            setattr(album, key, value)
        self.session.add(album)
        self.session.commit()
        self.session.refresh(album)
        return album

    def upsert(self, entity: Album) -> Album:
        """Insert, or merge only the fields the caller set. Returns the managed row."""
        existing = self.session.get(Album, entity.id)
        if existing is None:
            self.session.add(entity)
            return entity
        for key, value in entity.model_dump(exclude={"id"}, exclude_unset=True).items():
            setattr(existing, key, value)
        self.session.add(existing)
        return existing

    def delete(self, id: str) -> bool:
        """Delete by id. Returns True if a row was removed, False if not found."""
        album = self.session.get(Album, id)
        if album is None:
            return False
        self.session.delete(album)
        self.session.commit()
        return True
