import pytest

from spotify_to_ytmusic.spotify import Spotify


class TestSpotify:
    @pytest.fixture(autouse=True)
    def fixture_spotify(self):
        self.spotify = Spotify()

    def test_getSpotifyPlaylist(self):
        data = self.spotify.getSpotifyPlaylist(
            "https://open.spotify.com/playlist/03ICMYsVsC4I2SZnERcQJb"
        )
        assert len(data) == 3
        assert len(data["tracks"]) > 190

    def test_getUserPlaylists(self):
        # Spotify only allows listing the logged-in user's playlists
        user = self.spotify.api.me()["id"]
        playlists = self.spotify.getUserPlaylists(user)
        assert all(p["owner"]["id"] == user for p in playlists)
