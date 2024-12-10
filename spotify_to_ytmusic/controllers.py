import json
import os
import re
import tempfile
import time
from datetime import datetime

import spotipy

from spotify_to_ytmusic.setup import setup as setup_func
from spotify_to_ytmusic.spotify import Spotify
from spotify_to_ytmusic.ytmusic import YTMusicTransfer


def _get_spotify_playlist(spotify, playlist):
    try:
        return spotify.getSpotifyPlaylist(playlist)
    except Exception as ex:
        print(
            "Could not get Spotify playlist. Please check the playlist link.\n Error: " + repr(ex)
        )
        return


def _print_success(name, playlistId):
    print(
        f"Success: created playlist '{name}' at\n"
        f"https://music.youtube.com/playlist?list={playlistId}"
    )


def _init():
    return Spotify(), YTMusicTransfer()

def get_common_args_for_extended_search(args):
    return {
            "extended_search": args.extended_search,
            "confidence": args.confidence,
            "use_cached": args.use_cached,
            "search_albums": args.search_albums,
            "enable_fallback": args.enable_fallback
    }

def all(args):
    spotify, ytmusic = _init()
    pl = spotify.getUserPlaylists(args.user)
    print(str(len(pl)) + " playlists found. Starting transfer...")
    count = 1
    for p in pl:
        print("Playlist " + str(count) + ": " + p["name"])
        count = count + 1
        try:
            playlist = spotify.getSpotifyPlaylist(p["external_urls"]["spotify"])
            videoIds = ytmusic.search_songs(
                playlist["tracks"],
                **get_common_args_for_extended_search(args)
            )
            playlist_id = ytmusic.create_playlist(
                p["name"],
                p["description"],
                "PUBLIC" if p["public"] else "PRIVATE",
                videoIds,
            )
            if args.like:
                for id in videoIds:
                    ytmusic.rate_song(id, "LIKE")
            _print_success(p["name"], playlist_id)
        except Exception as ex:
            print(f"Could not transfer playlist {p['name']}. {str(ex)}")


def _create_ytmusic(args, playlist, ytmusic):
    date = ""
    if args.date:
        date = " " + datetime.today().strftime("%m/%d/%Y")
    name = args.name + date if args.name else playlist["name"] + date
    info = playlist["description"] if (args.info is None) else args.info
    videoIds = ytmusic.search_songs(
                playlist["tracks"],
                **get_common_args_for_extended_search(args)
            )
    if args.like:
        for id in videoIds:
            ytmusic.rate_song(id, "LIKE")

    playlistId = ytmusic.create_playlist(
        name, info, "PUBLIC" if args.public else "PRIVATE", videoIds
    )
    _print_success(name, playlistId)


def create(args):
    spotify, ytmusic = _init()
    playlist = _get_spotify_playlist(spotify, args.playlist)
    _create_ytmusic(args, playlist, ytmusic)


def liked(args):
    spotify, ytmusic = _init()
    if not isinstance(spotify.api.auth_manager, spotipy.SpotifyOAuth):
        raise Exception("OAuth not configured, please run setup and set OAuth to 'yes'")
    playlist = spotify.getLikedPlaylist()
    _create_ytmusic(args, playlist, ytmusic)


def update(args):
    spotify, ytmusic = _init()

    if args.playlist != "liked":
        playlist = _get_spotify_playlist(spotify, args.playlist)
    else:
        playlist = spotify.getLikedPlaylist()

    print("Note: If you receive 400 HTTP error and you are using cached mode, you may have an invalid videoID in your lookup file. Try clearing the cache, it may help.")

    playlistId = ytmusic.get_playlist_id(args.name)
    videoIds = ytmusic.search_songs(
                playlist["tracks"],
                **get_common_args_for_extended_search(args)
            )
    if not args.append:
        ytmusic.remove_songs(playlistId)
    time.sleep(2)
    ytmusic.add_playlist_items(playlistId, videoIds)


def remove(args):
    ytmusic = YTMusicTransfer()
    ytmusic.remove_playlists(args.pattern)

def search(args):
    spotify, ytmusic = _init()
    track = spotify.getSingleTrack(args.link)
    tracks = {
        "name": track["name"],
        "artist": ", ".join([artist["name"] for artist in track["artists"]]),
        "duration": track["duration_ms"] / 1000,
        "album": track['album']['name'],
        "artists_list": [artist["name"] for artist in track["artists"] if "name" in artist],
        "is_explicit": track["explicit"]
    }

    video_id = ytmusic.search_songs(
                [tracks],
                **get_common_args_for_extended_search(args)
            )
    if video_id:
        print(f"https://music.youtube.com/watch?v={video_id[0]}")
    else:
        print("No match found")

def setup(args):
    setup_func(args.file)

def cache_clear(args):
    path = os.path.dirname(os.path.realpath(__file__))
    lookup_path = os.path.join(path, "lookup.json")
    
    print(f"Removing File: {lookup_path}")
    
    if os.path.exists(lookup_path):
        os.remove(lookup_path)

def fix_match(args):
    existing_id = args.current_id
    new_id = args.new_id

    print(f"Replacing {existing_id} with {new_id}")
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lookup.json")

    if not os.path.exists(path):
        print(f"Error: {path} does not exist.")
        return

    try:
        with open(path, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                print("Error: lookup.json must contain a dictionary.")
                return
    except json.JSONDecodeError:
        print("Error: lookup.json contains invalid JSON.")
        return

    if not data:
        print("Error: lookup.json is empty.")
        return
    
    found = False
    for key, value in data.items():
        if value == existing_id:
            print(f"Track: {key}")
            data[key] = new_id
            found = True
            break

    if found:
        try:
            with tempfile.NamedTemporaryFile("w", delete=False, dir=os.path.dirname(path), encoding="utf-8") as tmpfile:
                json.dump(data, tmpfile, ensure_ascii=False, indent=4)
                temp_path = tmpfile.name

            os.replace(temp_path, path)
            print(f"Replaced {existing_id} with {new_id} in lookup.json")
        except Exception as e:
            print(f"Error: Failed to write changes to lookup.json. {e}")
    else:
        print(f"{existing_id} not found in lookup.json")
    