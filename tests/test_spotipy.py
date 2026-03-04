import json
import pytest
from pathlib import Path
from unittest import mock


from spotify_to_ytmusic.spotify import Spotify


class TestSpotify:
    @pytest.fixture(autouse=True)
    def fixture_spotify(self, mock_spotify_api):
        self.spotify = Spotify()
    
    @pytest.fixture
    def spotify_playlist_json(self):
        mocked_playlist_response_path = Path(__file__).parent / "mock_fixtures" / "mocked_get_large_playlist_response.json"
        with mocked_playlist_response_path.open() as f:
            return json.load(f)

    @pytest.fixture
    def spotify_all_playlists_json(self):
        mocked_playlist_response_path = Path(__file__).parent / "mock_fixtures" / "mocked_get_user_playlists_response.json"
        with mocked_playlist_response_path.open() as f:
            return json.load(f)

    @pytest.fixture
    def spotify_playlist_items_page_2_json(self):
        mocked_playlist_response_path = Path(__file__).parent / "mock_fixtures" / "mocked_get_large_playlist_items_response_page_2.json"
        with mocked_playlist_response_path.open() as f:
            return json.load(f)

    @pytest.fixture
    def spotify_playlist_items_page_3_json(self):
        mocked_playlist_response_path = Path(__file__).parent / "mock_fixtures" / "mocked_get_large_playlist_items_response_page_3.json"
        with mocked_playlist_response_path.open() as f:
            return json.load(f)

    @pytest.fixture(autouse=True)
    def mock_spotify_api(self, spotify_playlist_json, spotify_all_playlists_json, spotify_playlist_items_page_2_json, spotify_playlist_items_page_3_json):
        with mock.patch("spotify_to_ytmusic.spotify.spotipy.Spotify") as MockSpotipy:
            self.mock_client = MockSpotipy.return_value

            self.mock_client.playlist.return_value = spotify_playlist_json
            self.mock_client.user_playlists.return_value = spotify_all_playlists_json
            self.mock_client.playlist_items.side_effect = [spotify_playlist_items_page_2_json, spotify_playlist_items_page_3_json]

            yield self.mock_client

    def test_getSpotifyPlaylist(self, mock_spotify_api):
        with open("/home/easotelo1/dev/python/git/spotify_to_ytmusic/tests/mock_fixtures/mocked_get_large_playlist_response.json") as f:
            data = json.load(f)
        data = self.spotify.getSpotifyPlaylist(
            "https://open.spotify.com/playlist/03ICMYsVsC4I2SZnERcQJb"
        )
        assert len(data) == 3
        assert len(data["tracks"]) > 190
    
    def test_getUserPlaylists(self):
        playlists = self.spotify.getUserPlaylists("testUser")
        assert len(playlists) > 40
