import unittest

from spotify_to_ytmusic.spotify import Spotify


class TestSpotify(unittest.TestCase):

    def setUp(self) -> None:
        self.spotify = Spotify()

    def test_getSpotifyPlaylist(self):
        data = self.spotify.getSpotifyPlaylist("https://open.spotify.com/playlist/03ICMYsVsC4I2SZnERcQJb")
        self.assertEqual(len(data), 3)
        self.assertGreater(len(data["tracks"]), 190)

    def test_getUserPlaylists(self):
        playlists = self.spotify.getUserPlaylists("spinninrecordsofficial")
        self.assertGreater(len(playlists), 50)
