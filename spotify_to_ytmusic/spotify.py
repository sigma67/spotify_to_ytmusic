import html
import re
import string

import spotipy
from spotipy import CacheFileHandler
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from spotify_to_ytmusic.settings import SPOTIPY_CACHE_FILE, Settings
from spotify_to_ytmusic.utils.browser import has_browser


class Spotify:
    def __init__(self):
        settings = Settings()
        conf = settings["spotify"]
        client_id = conf["client_id"]

        assert set(client_id).issubset(string.hexdigits), (
            f"Spotify client_id not set or invalid: {client_id}"
        )
        client_secret = conf["client_secret"]
        assert set(client_secret).issubset(string.hexdigits), (
            f"Spotify client_secret not set or invalid: {client_secret}"
        )

        use_oauth = conf.getboolean("use_oauth")

        cache_handler = CacheFileHandler(cache_path=SPOTIPY_CACHE_FILE.as_posix())
        if use_oauth:
            auth = SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri="https://127.0.0.1",
                scope="user-library-read",
                cache_handler=cache_handler,
                open_browser=has_browser(),
            )
            self.api = spotipy.Spotify(auth_manager=auth)
        else:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret,
                cache_handler=cache_handler,
            )
            self.api = spotipy.Spotify(
                client_credentials_manager=client_credentials_manager
            )

    def getSpotifyPlaylist(self, url):
        playlistId = extract_playlist_id_from_url(url)

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

    def getLikedPlaylist(self):
        response = self.api.current_user_saved_tracks(limit=50)
        tracks = response["items"]
        while response["next"] is not None:
            response = self.api.current_user_saved_tracks(
                limit=50, offset=response["offset"] + 50
            )
            tracks.extend(response["items"])

        return {
            "tracks": build_results(tracks),
            "name": "Liked songs (Spotify)",
            "description": "Your liked tracks from spotify",
        }

    def getSingleTrack(self, song_url):
        return self.api.track(song_url)


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


def extract_playlist_id_from_url(url: str) -> str:
    if match := re.search(r"playlist\/(?P<id>\w{22})\W?", url):
        return match.group("id")
    elif match := re.search(r"playlist\/(?P<id>\w+)\W?", url):
        id = match.group("id")
        raise ValueError(
            f"Bad playlist id: {id}\nA playlist id should be 22 characters long, not {len(id)}"
        )
    else:
        raise ValueError(
            f"Couldn't understand playlist url: {url}\nA playlist url should look like this: https://open.spotify.com/playlist/37i9dQZF1DZ06evO41HwPk"
        )
