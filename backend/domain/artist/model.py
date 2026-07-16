from sqlmodel import Field, SQLModel

# if TYPE_CHECKING:
# from domain.album.model import Album
# from domain.track.model import Track


class ArtistBase(SQLModel):
    name: str = Field(unique=True, index=True)
    image_url: str | None = None

    spotify_id: str | None = None
    spotify_url: str | None = None

    # Relationships
    # albums: list["Album"] = Relationship(back_populates="artist")
    # tracks: list["Track"] = Relationship(back_populates="author")

    # Domain logic lives on the model, not scattered in routes
    # def total_albums(self) -> int:
    #     return self.albums.__len__()

    # def total_tracks(self) -> int:
    #     return self.tracks.__len__


class Artist(ArtistBase, table=True):
    id: str = Field(primary_key=True)
