"""Functionality tests for libs.music_library.utils."""

from libs.music_library.utils import extract_featured_artists_from_name


class TestLibraryUtils:
    def test_extracts_single_artist(self):
        variants = [
            # "Song Title featuring Artist",
            "Song Title (featuring Artist)",
            "Song Title [featuring Artist]",
            # "Song Title feat. Artist",
            "Song Title (feat. Artist)",
            "Song Title [feat. Artist]",
            "Song Title (part 2) [feat. Artist]",
        ]
        for case in variants:
            assert extract_featured_artists_from_name(case) == ["Artist"]

    # def test_extracts_multiple_artist(self):
    #     variants = [
    #         "Song Title feat. One, Two & Three",
    #         "Song Title feat. One & Two",
    #     ]
    #     for case in variants:
    #         assert extract_featured_artists_from_name(case) == ["Artist"]

    def test_ignores_no_artists(self):
        assert extract_featured_artists_from_name("Song title (part ii)") is None
