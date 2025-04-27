import pytest

from spotify_to_ytmusic.spotify import extract_playlist_id_from_url


class TestParsing:
    def test_idFromSpotifyUrl(self):
        url = "https://open.spotify.com/playlist/37i9dQZF1DX5KpP2LN299J"
        assert extract_playlist_id_from_url(url) == "37i9dQZF1DX5KpP2LN299J"

    def test_idFromSpotifyUrlWithShareId(self):
        url = "http://open.spotify.com/playlist/37i9dQZF1DZ06evO3siF1W?si=grips"
        assert extract_playlist_id_from_url(url) == "37i9dQZF1DZ06evO3siF1W"

    def test_idFromSpotifyUrlRejectBadId(self):
        url = "https://open.spotify.com/playlist/420"
        with pytest.raises(ValueError, match=r"Bad playlist id"):
            extract_playlist_id_from_url(url)

    def test_idFromSpotifyUrlRejectBadUrl(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        with pytest.raises(ValueError):
            extract_playlist_id_from_url(url)
