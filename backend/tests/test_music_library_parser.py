"""Characterisation tests for libs.music_library.parser.

These pin the current behaviour of the public functions (parse_library,
extract_albums, extract_artists) against fixtures/sample_library.xml so the
parser can be refactored safely.
"""

import plistlib
from pathlib import Path

import pytest
from sqlalchemy import Null

from libs.music_library.parser import MusicLibraryParser

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_library.xml"


@pytest.fixture(scope="module")
def library_parser_fixture() -> MusicLibraryParser:
    return MusicLibraryParser(FIXTURE_PATH)


def track_by_id(tracks: list[dict], persistent_id: str) -> dict:
    return next(t for t in tracks if t["id"] == persistent_id)


def make_parser(tracks: list[dict]) -> MusicLibraryParser:
    # skip __init__, no file needed
    parser = MusicLibraryParser.__new__(MusicLibraryParser)
    parser.parsed_tracks = tracks
    return parser


class TestParseLibrary:
    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            MusicLibraryParser(tmp_path / "nope.xml")

    def test_parses_all_tracks(self, library_parser_fixture: MusicLibraryParser):
        assert len(library_parser_fixture.get_tracks()) == 17

    def test_maps_full_track(self, library_parser_fixture: MusicLibraryParser):
        # Wonderwall — has every field the parser maps.
        parsed_tracks = library_parser_fixture.get_tracks()
        track = track_by_id(parsed_tracks, "875F57138A9A149E")
        assert track == {
            "id": "875F57138A9A149E",
            "name": "Wonderwall",
            "artist": "Oasis",
            "album_artist": "Oasis",
            "album": "Time Flies... 1994–2009",
            "genre": "Rock",
            "year": 2010,
            "track_id": 4052,
            "track_number": 8,
            "track_length": 260519,
            "date_added": "2012-03-29T20:23:01",
            "last_played": "2024-08-06T10:14:10",
            "play_count": 385,
            "album_rating": 60,
            "album_rating_computed": True,
            "compilation": False,
        }

    def test_compilation_flag(self, library_parser_fixture: MusicLibraryParser):
        parsed_tracks = library_parser_fixture.get_tracks()
        sunflower = track_by_id(parsed_tracks, "49B2579F7514DB60")
        assert sunflower["compilation"] is True
        assert sunflower["album_artist"] == "Various Artists"

    def test_absent_rating_fields_are_none(
        self, library_parser_fixture: MusicLibraryParser
    ):
        # Pond track has no Album Rating / Album Rating Computed keys.
        parsed_tracks = library_parser_fixture.get_tracks()
        track = track_by_id(parsed_tracks, "08FFAFD928568233")
        assert track["album_rating"] is None
        assert track["album_rating_computed"] is None
        assert track["compilation"] is False

    def test_dates_are_iso_strings(self, library_parser_fixture: MusicLibraryParser):
        parsed_tracks = library_parser_fixture.get_tracks()
        for track in parsed_tracks:
            assert isinstance(track["date_added"], str)
            assert "T" in track["date_added"]

    def test_sparse_track_defaults(self, tmp_path):
        library = {
            "Tracks": {
                "100": {
                    "Track ID": 100,
                    "Name": "Oblivion",
                    "Artist": "Grimes",
                }
            }
        }
        xml_path = tmp_path / "sparse.xml"
        with xml_path.open("wb") as fh:
            plistlib.dump(library, fh)

        parser = MusicLibraryParser(xml_path)
        (track,) = parser.get_tracks()
        assert track["id"] == ""
        assert track["name"] == "Oblivion"
        assert track["artist"] == "Grimes"
        assert track["album"] == ""
        assert track["album_artist"] == ""
        assert track["genre"] == ""
        assert track["year"] is None
        assert track["track_id"] == 100
        # Current behaviour: a missing/zero Track Number falls back to
        # sqlalchemy's Null type via `int(...) or Null`.
        assert track["track_number"] is Null
        assert track["track_length"] == 0
        assert track["date_added"] is None
        assert track["last_played"] is None
        assert track["play_count"] == 0
        assert track["compilation"] is False


class TestExtractAlbums:
    def test_dedupes_by_album_artist_and_album(
        self, library_parser_fixture: MusicLibraryParser
    ):
        albums = library_parser_fixture.get_albums()
        keys = [(a["album_artist"], a["album"]) for a in albums]
        assert len(keys) == len(set(keys)) == 12

    def test_same_album_name_different_artists_kept_separate(
        self, library_parser_fixture: MusicLibraryParser
    ):
        albums = library_parser_fixture.get_albums()
        various = [a for a in albums if a["album_artist"] == "Various Artists"]
        assert {a["album"] for a in various} == {
            "Top 40 Singles 2008",
            "Spider-Man: Into the Spider-Verse",
            "The Umbrella Academy",
        }

    def test_album_fields(self, library_parser_fixture: MusicLibraryParser):
        albums = library_parser_fixture.get_albums()
        gkmc = next(a for a in albums if a["album"] == "good kid, m.A.A.d city")
        assert gkmc == {
            "artist": "Kendrick Lamar",
            "album": "good kid, m.A.A.d city",
            "album_artist": "Kendrick Lamar",
            "genre": "Hip Hop",
            "year": 2012,
            "date_added": "2013-02-07T17:45:10",
            "album_rating": 80,
            "album_rating_computed": None,
            "compilation": False,
        }

    def test_skips_tracks_without_album(self):
        tracks = [
            {"album": "", "album_artist": "Grimes", "artist": "Grimes"},
            {"album_artist": "Grimes", "artist": "Grimes"},
            {"album": "Art Angels", "album_artist": "Grimes", "artist": "Grimes"},
        ]
        parser = make_parser(tracks)
        albums = parser.get_albums()
        assert len(albums) == 1
        assert albums[0]["album"] == "Art Angels"

    def test_last_track_wins_on_duplicates(self):
        # Current behaviour: unique_by overwrites on repeated keys, so the
        # last track's values win (its docstring claims first-wins).
        tracks = [
            {"album": "Art Angels", "album_artist": "Grimes", "genre": "Electronic"},
            {"album": "Art Angels", "album_artist": "Grimes", "genre": "Pop"},
        ]
        parser = make_parser(tracks)
        (album,) = parser.get_albums()
        assert album["genre"] == "Pop"


class TestExtractArtists:
    def test_dedupes_by_album_artist(self, library_parser_fixture: MusicLibraryParser):
        artists = library_parser_fixture.get_artists()
        names = [a["album_artist"] for a in artists]
        assert len(names) == len(set(names)) == 9
        assert set(names) == {
            "Begin Again Cast",
            "P!nk",
            "Kendrick Lamar",
            "Kano",
            "Various Artists",
            "Pond",
            "Oasis",
            "HAIM",
            "Grimes",
        }

    def test_artist_fields(self, library_parser_fixture: MusicLibraryParser):
        artists = library_parser_fixture.get_artists()
        haim = next(a for a in artists if a["album_artist"] == "HAIM")
        assert haim == {"album_artist": "HAIM", "artist": "HAIM"}

    def test_skips_tracks_without_album_artist(self):
        tracks = [
            {"album_artist": "", "artist": "Adam Levine"},
            {"artist": "Adam Levine"},
        ]
        parser = make_parser(tracks)
        assert parser.get_artists() == []
