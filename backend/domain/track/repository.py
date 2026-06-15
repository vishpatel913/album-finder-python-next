from abc import ABC, abstractmethod

from sqlmodel import Session, select

from .model import Track


class AbstractTrackRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> Track | None: ...

    @abstractmethod
    def list(self) -> list[Track]: ...

    @abstractmethod
    def update(self, id: str, fields: dict) -> Track | None: ...


class SqlTrackRepository(AbstractTrackRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: str) -> Track | None:
        return self.session.get(Track, id)

    def list(self) -> list[Track]:
        return self.session.exec(select(Track)).all()

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
