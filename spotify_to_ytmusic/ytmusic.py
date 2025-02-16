import json
import os
from pathlib import Path
import re
from collections import OrderedDict

from ytmusicapi import YTMusic
from ytmusicapi.auth.oauth import OAuthCredentials

from spotify_to_ytmusic.utils.match import get_best_fit_song_id, get_best_fit_song_id_v2, normalize_text
from spotify_to_ytmusic.settings import Settings

path = os.path.dirname(os.path.realpath(__file__)) + os.sep


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

    def load_lookup_table(self):
        try:
            with open(path + "lookup.json") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_to_lookup_table(self, table):
        with open(path + "lookup.json", 'w', encoding="utf-8") as f:
            json.dump(table, f, ensure_ascii=False, indent=4)
        
    def search_songs(self, tracks, **kawgs):
        
        extended_search = kawgs.pop("extended_search", False)
        confidence = kawgs.get("confidence", None)
        use_cached = kawgs.pop("use_cached", False)
        search_albums = kawgs.get("search_albums", False)
        enable_fallback = kawgs.get("enable_fallback", False)

        videoIds = []
        songs = list(tracks)
        notFound = list()

        if use_cached:
            lookup_ids = self.load_lookup_table()
        
        if extended_search:
            print(f"Extended search enabled! Confidence level: {confidence if confidence else 0.7} | Use Cached: {use_cached} | Search Albums: {search_albums} | Fallback: {'Enabled' if enable_fallback else 'Disabled'}")
            
        print("Searching YouTube...")
        for i, song in enumerate(songs):
            name = re.sub(r" \(feat.*\..+\)", "", song["name"])
            query = song["artist"] + " " + name
            query = query.replace(" &", "")

            name_for_extended_search = normalize_text(song["name"])
            artist_for_extended_search = normalize_text(" ".join(song["artists_list"]))
            query_for_extended_search = artist_for_extended_search + " " + name_for_extended_search
            
            if use_cached and (query in lookup_ids.keys() or query_for_extended_search in lookup_ids.keys()):
                print(f"Found cached link from lookup table for {song['name']}\n")
                videoIds.append(lookup_ids[query] if query in lookup_ids.keys() else lookup_ids[query_for_extended_search])
                continue
            if not extended_search:
                result = self.api.search(query)
            else:
                result = self.api.search(query_for_extended_search)
            if len(result) == 0:
                notFound.append(query)
            else:
                if not extended_search:
                    targetSong = get_best_fit_song_id(result, song)
                else:
                    targetSong = get_best_fit_song_id_v2(ytm_results=result, spoti=song, **kawgs, api=self.api)
                
                if targetSong is None:
                    notFound.append(query)
                else:
                    videoIds.append(targetSong)
                    if use_cached:
                        lookup_ids[query] = targetSong
                        self.save_to_lookup_table(lookup_ids)

            if i > 0 and i % 10 == 0:
                print(f"YouTube tracks: {i}/{len(songs)}")

        with open(path + "noresults_youtube.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(notFound))
            f.write("\n")
            f.close()

        return videoIds

    def add_playlist_items(self, playlistId, videoIds):
        videoIds = OrderedDict.fromkeys(videoIds)
        self.api.add_playlist_items(playlistId, videoIds)

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


    def remove_songs(self, playlistId):
        items = self.api.get_playlist(playlistId, 10000)
        if "tracks" in items and items["tracks"]:
            self.api.remove_playlist_items(playlistId, items["tracks"])

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
