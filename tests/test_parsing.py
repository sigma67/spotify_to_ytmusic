import unittest

from spotify_to_ytmusic.spotify import Spotify


class TestParsing(unittest.TestCase):
    def test_idFromSpotifyUrl(self):
        url = "https://open.spotify.com/playlist/37i9dQZF1DX5KpP2LN299J"
        self.assertEqual(Spotify.getPlaylistIdFromUrl(url), "37i9dQZF1DX5KpP2LN299J")

    def test_idFromSpotifyUrlWithShareId(self):
        url = "http://open.spotify.com/playlist/37i9dQZF1DZ06evO3siF1W?si=grips"
        self.assertEqual(Spotify.getPlaylistIdFromUrl(url), "37i9dQZF1DZ06evO3siF1W")

    def test_idFromSpotifyUrlRejectBadId(self):
        url = "https://open.spotify.com/playlist/420"
        self.assertRaises(ValueError, Spotify.getPlaylistIdFromUrl, url)
    
    def test_idFromSpotifyUrlRejectBadUrl(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertRaises(ValueError, Spotify.getPlaylistIdFromUrl, url)
