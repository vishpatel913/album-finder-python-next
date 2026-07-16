from __future__ import annotations

import logging
import plistlib
from datetime import datetime
from pathlib import Path

from utils.unique import unique_by

logger = logging.getLogger(__name__)


class MusicLibraryParser:
    def __init__(self, library_xml_path: Path):
        self.library_xml_path = library_xml_path
        self.parsed_tracks = self.__parse_library()

    def get_tracks(self) -> list[dict]:
        return self.parsed_tracks

    def get_albums(self) -> list[dict]:
        albums = (
            self.__get_album_from_track(t) for t in self.parsed_tracks if t.get("album")
        )
        return unique_by(albums, key=lambda a: (a["album_artist"], a["album"]))

    def get_artists(self) -> list[dict]:
        artists = (
            self.__get_artist_from_track(t)
            for t in self.parsed_tracks
            if t.get("album_artist")
        )
        return unique_by(artists, key=lambda a: a["album_artist"])

    def __parse_library(self) -> list[dict]:
        xml_path = Path(self.library_xml_path).expanduser()
        if not xml_path.exists():
            raise FileNotFoundError(f"Library XML not found: {xml_path}")

        with xml_path.open("rb") as fh:
            library = plistlib.load(fh)

        raw_tracks = library.get("Tracks", {})
        result: list[dict] = []

        for raw in raw_tracks.values():
            track = self.__parse_track(raw)

            result.append(track)

        return result

    def __parse_track(self, track: dict) -> dict:
        name = track.get("Name", "")
        # featured = _extract_featured(name)
        return {
            "id": track.get("Persistent ID", ""),
            "name": name,
            "artist": track.get("Artist", ""),
            "album_artist": track.get("Album Artist", ""),
            "album": track.get("Album", ""),
            "genre": track.get("Genre", ""),
            "year": track.get("Year"),
            "track_id": int(track.get("Track ID", 0)) or None,
            "track_number": int(track.get("Track Number", 0)) or None,
            "disc_number": int(track.get("Disc Number", 0)) or None,
            "track_length": int(track.get("Total Time", 0) or 0),
            "date_added": self.__iso(track.get("Date Added")),
            "last_played": self.__iso(track.get("Play Date UTC")),
            "play_count": int(track.get("Play Count", 0) or 0),
            "album_rating": track.get("Album Rating"),  # 0-100 in iTunes XML
            "album_rating_computed": track.get(
                "Album Rating Computed"
            ),  # 0-100 in iTunes XML
            "compilation": bool(track.get("Compilation", False)),
        }

    def __get_album_from_track(self, track: dict) -> dict:
        return {
            "artist": track.get("artist", ""),
            "album": track.get("album", ""),
            "album_artist": track.get("album_artist", ""),
            "genre": track.get("genre", ""),
            "year": track.get("year"),
            "date_added": track.get("date_added"),
            "album_rating": track.get("album_rating"),  # 0-100 in iTunes XML
            "album_rating_computed": track.get("album_rating_computed"),  # 0-100
            "compilation": self.__is_track_compilation(track),
        }

    def __get_artist_from_track(self, track: dict) -> dict:
        return {
            "album_artist": track.get("album_artist", ""),
            "artist": track.get("artist", ""),
        }

    def __is_track_compilation(self, track: dict) -> bool:
        return bool(track.get("compilation", False))

    def __iso(self, value) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)
