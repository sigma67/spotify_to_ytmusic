import os
import re
from collections import OrderedDict
import sys
import time

import requests
from ytmusicapi import YTMusic
from ytmusicapi.auth.oauth import OAuthCredentials
from ytmusicapi.exceptions import YTMusicServerError

from spotify_to_ytmusic.utils.match import get_best_fit_song_id
from spotify_to_ytmusic.settings import Settings

from spotify_to_ytmusic.utils.cache_manager import CacheManager

path = os.path.dirname(os.path.realpath(__file__)) + os.sep

cacheManager = CacheManager()


class YTMusicTransfer:
    def __init__(self):
        settings = Settings()
        headers = settings["youtube"]["headers"]
        assert headers.startswith("{"), "ytmusicapi headers not set or invalid"
        oauth_credentials = (
            None
            if settings["youtube"]["auth_type"] != "oauth"
            else OAuthCredentials(
                client_id=settings["youtube"]["client_id"],
                client_secret=settings["youtube"]["client_secret"],
            )
        )
        self.api = YTMusic(
            headers, settings["youtube"]["user_id"], oauth_credentials=oauth_credentials
        )

    def create_playlist(self, name, info, privacy="PRIVATE", tracks=None):
        return self.api.create_playlist(name, info, privacy, video_ids=tracks)

    def rate_song(self, id, rating):
        return self.api.rate_song(id, rating)

    def search_songs(self, tracks, use_cached: bool = False):
        videoIds = []
        songs = list(tracks)
        notFound = list()
        lookup_ids = cacheManager.load_lookup_table()

        if use_cached:
            print("Use of cache file is enabled.")

        print("Searching YouTube...")
        for i, song in enumerate(songs):
            name = re.sub(r" \(feat.*\..+\)", "", song["name"])
            query = song["artist"] + " " + name
            query = query.replace(" &", "")

            if use_cached and query in lookup_ids.keys():
                videoIds.append(lookup_ids[query])
                continue

            result = self.api.search(query)

            if len(result) == 0:
                notFound.append(query)
            else:
                targetSong = get_best_fit_song_id(result, song)
                if targetSong is None:
                    notFound.append(query)
                else:
                    videoIds.append(targetSong)
                    if use_cached:
                        lookup_ids[query] = targetSong
                        cacheManager.save_to_lookup_table(lookup_ids)

            if i > 0 and i % 10 == 0:
                print(f"YouTube tracks: {i}/{len(songs)}")

        with open(path + "noresults_youtube.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(notFound))
            f.write("\n")
            f.close()

        return videoIds

    def add_playlist_items(self, playlistId, videoIds, ignore_errors=True):
        videoIds = list(OrderedDict.fromkeys(videoIds))
        response = self.api.add_playlist_items(playlistId, videoIds)

        if response.get("status") == "STATUS_SUCCEEDED":
            return True

        if ignore_errors:
            problematic_ids = []

            for video_id in videoIds:
                individual_response = self.api.add_playlist_items(
                    playlistId, [video_id]
                )
                if individual_response.get("status") == "STATUS_FAILED":
                    problematic_ids.append(video_id)

            dialog_message = (
                response.get("actions", [{}])[0]
                .get("confirmDialogEndpoint", {})
                .get("content", {})
                .get("confirmDialogRenderer", {})
                .get("dialogMessages", [{}])[0]
                .get("runs", [{}])[0]
                .get("text", "")
            )

            dialog_duplicate_error = (
                response.get("actions", [{}])[0]
                .get("confirmDialogEndpoint", {})
                .get("content", {})
                .get("confirmDialogRenderer", {})
                .get("confirmButton", {})
                .get("buttonRenderer", {})
                .get("command", {})
                .get("playlistEditEndpoint", {})
                .get("actions", [{}])[0]
                .get("dedupeOption", "")
            )

            if dialog_message:
                print(f"Warning: {dialog_message}")
            if dialog_duplicate_error == "DEDUPE_OPTION_SKIP":
                print(
                    f"Warning: You have {len(problematic_ids)} duplicate IDs. This may be caused by the cache storing correct track IDs that are now redirecting to different track IDs. Try running the command without --use-cached or clear the cache to resolve this issue; otherwise, updating the playlist with --append may take longer each time."
                )
            videoIds = [vid for vid in videoIds if vid not in problematic_ids]

            if videoIds:
                return self.add_playlist_items(
                    playlistId, videoIds, ignore_errors=False
                )

        return False

    def get_playlist_id(self, name):
        pl = self.api.get_library_playlists(10000)
        try:
            playlist = next(x for x in pl if x["title"].find(name) != -1)["playlistId"]
            return playlist
        except StopIteration:
            raise Exception("Playlist title not found in playlists")

    def get_playlist_videoIds(self, playlistId):
        items = self.api.get_playlist(playlistId, 10000)
        if "tracks" in items and items["tracks"]:
            return [x["videoId"] for x in items["tracks"]]
        return []

    def remove_specified_tracks(self, playlistId, tracks):
        items = self.api.get_playlist(playlistId, 10000)

        if "tracks" in items and items["tracks"]:
            tracks_to_remove = [
                track for track in items["tracks"] if track.get("videoId") in tracks
            ]

            if tracks_to_remove:
                self.api.remove_playlist_items(playlistId, tracks_to_remove)

    def remove_songs(self, playlistId, max_retries=5, current_attempt=1):
        items = self.api.get_playlist(playlistId, 10000)

        if tracks := items.get("tracks"):
            if current_attempt == 1:
                print(f"Now removing {len(tracks)} tracks from YTMusic playlist...")

            try:
                self.api.remove_playlist_items(playlistId, tracks)
            except requests.exceptions.ReadTimeout:
                if current_attempt < max_retries:
                    time.sleep(2)
                    print(
                        f"Request timed out! Retrying ({current_attempt + 1}/{max_retries})..."
                    )
                    self.remove_songs(playlistId, max_retries, current_attempt + 1)
                else:
                    print("Max retries exhausted.")
                    sys.exit(0)
            except YTMusicServerError:
                pass

    def remove_playlists(self, pattern):
        playlists = self.api.get_library_playlists(10000)
        p = re.compile("{0}".format(pattern))
        matches = [pl for pl in playlists if p.match(pl["title"])]
        print("The following playlists will be removed:")
        print("\n".join([pl["title"] for pl in matches]))
        print("Please confirm (y/n):")

        choice = input().lower()
        if choice[:1] == "y":
            [self.api.delete_playlist(pl["playlistId"]) for pl in matches]
            print(str(len(matches)) + " playlists deleted.")
        else:
            print("Aborted. No playlists were deleted.")
