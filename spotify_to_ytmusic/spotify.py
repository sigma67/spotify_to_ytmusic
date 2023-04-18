import html
import string
from urllib.parse import urlparse

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from spotify_to_ytmusic.settings import Settings


class Spotify:
    def __init__(self):
        settings = Settings()
        conf = settings["spotify"]
        client_id = conf["client_id"]

        assert set(client_id).issubset(
            string.hexdigits
        ), f"Spotify client_id not set or invalid: {client_id}"
        client_secret = conf["client_secret"]
        assert set(client_secret).issubset(
            string.hexdigits
        ), f"Spotify client_secret not set or invalid: {client_secret}"

        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret
        )
        self.api = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def getSpotifyPlaylist(self, url):
        playlistId = get_id_from_url(url)
        if len(playlistId) != 22:
            raise Exception(f"Bad playlist id: {playlistId}")

        print("Getting Spotify tracks...")
        results = self.api.playlist(playlistId)
        name = results["name"]
        total = int(results["tracks"]["total"])
        tracks = build_results(results["tracks"]["items"])
        count = len(tracks)
        print(f"Spotify tracks: {count}/{total}")

        while count < total:
            more_tracks = self.api.playlist_items(playlistId, offset=count, limit=100)
            tracks += build_results(more_tracks["items"])
            count = count + 100
            print(f"Spotify tracks: {len(tracks)}/{total}")

        return {
            "tracks": tracks,
            "name": name,
            "description": html.unescape(results["description"]),
        }

    def getUserPlaylists(self, user):
        pl = self.api.user_playlists(user)["items"]
        count = 1
        more = len(pl) == 50
        while more:
            results = self.api.user_playlists(user, offset=count * 50)["items"]
            pl.extend(results)
            more = len(results) == 50
            count = count + 1

        return [p for p in pl if p["owner"]["id"] == user and p["tracks"]["total"] > 0]


def build_results(tracks, album=None):
    results = []
    for track in tracks:
        if "track" in track:
            track = track["track"]
        if not track or track["duration_ms"] == 0:
            continue
        album_name = album if album else track["album"]["name"]
        results.append(
            {
                "artist": " ".join([artist["name"] for artist in track["artists"]]),
                "name": track["name"],
                "album": album_name,
                "duration": track["duration_ms"] / 1000,
            }
        )

    return results


def get_id_from_url(url):
    url_parts = parse_url(url)
    return url_parts.path.split("/")[2]


def parse_url(url):
    return urlparse(url)
