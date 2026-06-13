from backend.domain.album.model import Album
from sqlmodel import Field, Relationship, SQLModel

# from backend.domain.track.model import Track


class ArtistBase(SQLModel):
    name: str = Field(unique=True, index=True)

    # Relationships
    albums: list["Album"] = Relationship(back_populates="author")
    # tracks: list["Track"] = Relationship(back_populates="author")

    # Domain logic lives on the model, not scattered in routes
    def total_albums(self) -> int:
        return self.albums.__len__()

    # def total_tracks(self) -> int:
    #     return self.tracks.__len__


class Artist(ArtistBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
