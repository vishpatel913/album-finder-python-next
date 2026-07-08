from abc import ABC, abstractmethod

from sqlmodel import Session, select

from .model import Track


class AbstractTrackRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> Track | None: ...

    @abstractmethod
    def list(self) -> list[Track]: ...

    @abstractmethod
    def create(self, entity: Track) -> Track: ...

    @abstractmethod
    def update(self, id: str, fields: dict) -> Track | None: ...

    @abstractmethod
    def upsert(self, entity: Track) -> Track: ...

    @abstractmethod
    def delete(self, id: str) -> bool: ...


class SqlTrackRepository(AbstractTrackRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: str) -> Track | None:
        return self.session.get(Track, id)

    def list(self) -> list[Track]:
        return list(self.session.exec(select(Track)).all())

    def create(self, entity: Track) -> Track:
        """Persist a new track and return the stored row."""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def update(self, id: str, fields: dict) -> Track | None:
        track = self.session.get(Track, id)
        if track is None:
            return None
        for key, value in fields.items():
            setattr(track, key, value)
        self.session.add(track)
        self.session.commit()
        self.session.refresh(track)
        return track

    def upsert(self, entity: Track) -> Track:
        """Insert, or merge only the fields the caller set. Returns the managed row."""
        existing = self.session.get(Track, entity.id)
        if existing is None:
            self.session.add(entity)
            return entity
        for key, value in entity.model_dump(exclude={"id"}, exclude_unset=True).items():
            setattr(existing, key, value)
        self.session.add(existing)
        return existing

    def delete(self, id: str) -> bool:
        """Delete by id. Returns True if a row was removed, False if not found."""
        track = self.session.get(Track, id)
        if track is None:
            return False
        self.session.delete(track)
        self.session.commit()
        return True
