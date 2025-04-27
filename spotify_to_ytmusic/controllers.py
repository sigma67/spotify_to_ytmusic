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
            "Could not get Spotify playlist. Please check the playlist link.\n Error: "
            + repr(ex)
        )
        return


def _print_success(name, playlistId):
    print(
        f"Success: created playlist '{name}' at\n"
        f"https://music.youtube.com/playlist?list={playlistId}"
    )


def _init():
    return Spotify(), YTMusicTransfer()


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
                playlist["tracks"], use_cached=args.use_cached
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
    videoIds = ytmusic.search_songs(playlist["tracks"], use_cached=args.use_cached)
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
    playlist = (
        spotify.getLikedPlaylist()
        if args.playlist == "liked"
        else _get_spotify_playlist(spotify, args.playlist)
    )
    playlistId = ytmusic.get_playlist_id(args.name)
    videoIds = ytmusic.search_songs(playlist["tracks"], use_cached=args.use_cached)

    if args.append:
        existingVideos = ytmusic.get_playlist_videoIds(playlistId)
        to_remove = (
            [vid for vid in existingVideos if vid not in videoIds]
            if args.remove_extra
            else []
        )
        to_add = [vid for vid in videoIds if vid not in existingVideos]

        if to_remove:
            ytmusic.remove_specified_tracks(playlistId, to_remove)
            time.sleep(2)
        if to_add:
            ytmusic.add_playlist_items(playlistId, to_add)
    else:
        if videoIds:
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
        "artist": track["artists"][0]["name"],
        "duration": track["duration_ms"] / 1000,
        "album": track["album"]["name"],
    }

    video_id = ytmusic.search_songs([tracks], use_cached=args.use_cached)

    if not video_id:
        print("Error: No Match found.")
        return
    print(f"https://music.youtube.com/watch?v={video_id[0]}")


def cache_clear(args):
    from spotify_to_ytmusic.utils.cache_manager import CacheManager

    cacheManager = CacheManager()
    cacheManager.remove_cache_file()


def setup(args):
    setup_func(args.file)
