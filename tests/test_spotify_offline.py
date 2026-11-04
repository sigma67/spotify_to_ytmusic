"""Tests for spotify.py that use a fake Spotify API, so no credentials are needed."""

import pytest
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from spotify_to_ytmusic.spotify import Spotify, build_results

TRACK = {
    "name": "Song",
    "artists": [{"name": "Artist"}],
    "album": {"name": "Album"},
    "duration_ms": 180000,
}


def make_playlist(owner, total, new_format=True):
    key = "items" if new_format else "tracks"
    return {"name": f"{owner}-{total}", "owner": {"id": owner}, key: {"total": total}}


class FakeApi:
    def __init__(self, pages, me="me", oauth=True):
        self.pages = pages
        self.me_id = me
        manager = SpotifyOAuth if oauth else SpotifyClientCredentials
        self.auth_manager = manager.__new__(manager)
        self.calls = []

    def me(self):
        return {"id": self.me_id}

    def current_user_playlists(self, limit=50, offset=0):
        self.calls.append(offset)
        index = offset // limit
        return {
            "items": self.pages[index],
            "next": "more" if index + 1 < len(self.pages) else None,
        }


def make_spotify(api):
    spotify = Spotify.__new__(Spotify)
    spotify.api = api
    return spotify


class TestGetUserPlaylists:
    def test_lists_own_non_empty_playlists_across_pages(self):
        pages = [
            [make_playlist("me", 3)] * 49 + [make_playlist("someone_else", 5)],
            [make_playlist("me", 0), make_playlist("me", 2, new_format=False)],
        ]
        api = FakeApi(pages)
        playlists = make_spotify(api).getUserPlaylists("me")
        assert len(playlists) == 50
        assert api.calls == [0, 50]

    def test_other_user_is_rejected(self):
        spotify = make_spotify(FakeApi([[]]))
        with pytest.raises(ValueError, match="logged-in user"):
            spotify.getUserPlaylists("spinninrecordsofficial")

    def test_requires_oauth(self):
        spotify = make_spotify(FakeApi([[]], oauth=False))
        with pytest.raises(ValueError, match="OAuth"):
            spotify.getUserPlaylists("me")


class TestBuildResults:
    def test_new_item_key(self):
        assert build_results([{"item": TRACK}])[0]["name"] == "Song"

    def test_legacy_track_key(self):
        assert build_results([{"track": TRACK}])[0]["name"] == "Song"

    def test_skips_entries_without_track(self):
        assert (
            build_results([{"item": None}, {"track": {**TRACK, "duration_ms": 0}}])
            == []
        )
