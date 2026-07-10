"""Characterisation tests for libs.music_library.parser.

These pin the current behaviour of the public functions (parse_library,
extract_albums, extract_artists) against fixtures/sample_library.xml so the
parser can be refactored safely.
"""

import plistlib
from pathlib import Path

import pytest
from sqlalchemy import Null

from libs.music_library.parser import extract_albums, extract_artists, parse_library

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_library.xml"


@pytest.fixture(scope="module")
def parsed_tracks() -> list[dict]:
    return parse_library(FIXTURE_PATH)


def track_by_id(tracks: list[dict], persistent_id: str) -> dict:
    return next(t for t in tracks if t["id"] == persistent_id)


class TestParseLibrary:
    def test_parses_all_tracks(self, parsed_tracks):
        assert len(parsed_tracks) == 17

    def test_maps_full_track(self, parsed_tracks):
        # Wonderwall — has every field the parser maps.
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

    def test_compilation_flag(self, parsed_tracks):
        sunflower = track_by_id(parsed_tracks, "49B2579F7514DB60")
        assert sunflower["compilation"] is True
        assert sunflower["album_artist"] == "Various Artists"

    def test_absent_rating_fields_are_none(self, parsed_tracks):
        # Pond track has no Album Rating / Album Rating Computed keys.
        track = track_by_id(parsed_tracks, "08FFAFD928568233")
        assert track["album_rating"] is None
        assert track["album_rating_computed"] is None
        assert track["compilation"] is False

    def test_dates_are_iso_strings(self, parsed_tracks):
        for track in parsed_tracks:
            assert isinstance(track["date_added"], str)
            assert "T" in track["date_added"]

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            parse_library(tmp_path / "nope.xml")

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

        (track,) = parse_library(xml_path)
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
    def test_dedupes_by_album_artist_and_album(self, parsed_tracks):
        albums = extract_albums(parsed_tracks)
        keys = [(a["album_artist"], a["album"]) for a in albums]
        assert len(keys) == len(set(keys)) == 12

    def test_same_album_name_different_artists_kept_separate(self, parsed_tracks):
        albums = extract_albums(parsed_tracks)
        various = [a for a in albums if a["album_artist"] == "Various Artists"]
        assert {a["album"] for a in various} == {
            "Top 40 Singles 2008",
            "Spider-Man: Into the Spider-Verse",
            "The Umbrella Academy",
        }

    def test_album_fields(self, parsed_tracks):
        albums = extract_albums(parsed_tracks)
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
        albums = extract_albums(tracks)
        assert len(albums) == 1
        assert albums[0]["album"] == "Art Angels"

    def test_last_track_wins_on_duplicates(self):
        # Current behaviour: unique_by overwrites on repeated keys, so the
        # last track's values win (its docstring claims first-wins).
        tracks = [
            {"album": "Art Angels", "album_artist": "Grimes", "genre": "Electronic"},
            {"album": "Art Angels", "album_artist": "Grimes", "genre": "Pop"},
        ]
        (album,) = extract_albums(tracks)
        assert album["genre"] == "Pop"


class TestExtractArtists:
    def test_dedupes_by_album_artist(self, parsed_tracks):
        artists = extract_artists(parsed_tracks)
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

    def test_artist_fields(self, parsed_tracks):
        artists = extract_artists(parsed_tracks)
        haim = next(a for a in artists if a["album_artist"] == "HAIM")
        assert haim == {"album_artist": "HAIM", "artist": "HAIM"}

    def test_skips_tracks_without_album_artist(self):
        tracks = [
            {"album_artist": "", "artist": "Adam Levine"},
            {"artist": "Adam Levine"},
        ]
        assert extract_artists(tracks) == []
