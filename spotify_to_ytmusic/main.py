import argparse
import sys
from datetime import datetime
from pathlib import Path

from spotify_to_ytmusic.setup import setup
from spotify_to_ytmusic.spotify import Spotify
from spotify_to_ytmusic.ytmusic import YTMusicTransfer


def get_args(args=None):
    parser = argparse.ArgumentParser(description="Transfer spotify playlist to YouTube Music.")

    subparsers = parser.add_subparsers(help="Provide a subcommand", dest="command")
    setup_parser = subparsers.add_parser("setup", help="Set up credentials")
    setup_parser.add_argument("--file", type=Path, help="Optional path to a settings.ini file")

    playlist_creator = argparse.ArgumentParser(add_help=False)
    playlist_creator.add_argument(
        "-p",
        "--public",
        action="store_true",
        help="Make created playlist public. Default: private",
    )

    create_parser = subparsers.add_parser(
        "create",
        help="Create a new playlist on YouTube Music.",
        parents=[playlist_creator],
    )
    create_parser.add_argument("playlist", type=str, help="Provide a playlist Spotify link.")
    create_parser.add_argument(
        "-d",
        "--date",
        action="store_true",
        help="Append the current date to the playlist name",
    )
    create_parser.add_argument(
        "-i",
        "--info",
        type=str,
        help="Provide description information for the YouTube Music Playlist. Default: Spotify playlist description",
    )
    create_parser.add_argument(
        "-n",
        "--name",
        type=str,
        help="Provide a name for the YouTube Music playlist. Default: Spotify playlist name",
    )

    update_parser = subparsers.add_parser(
        "update",
        help="Delete all entries in the provided Google Play Music playlist and update the playlist with entries from the Spotify playlist.",
    )
    update_parser.add_argument(
        "name", type=str, help="The name of the YouTube Music playlist to update."
    )
    update_parser.add_argument(
        "--append", help="Do not delete items, append to target playlist instead"
    )

    remove_parser = subparsers.add_parser(
        "remove", help="Remove playlists with specified regex pattern."
    )
    remove_parser.add_argument("pattern", help="regex pattern")

    all_parser = subparsers.add_parser(
        "all",
        help="Transfer all public playlists of the specified user (Spotify User ID).",
        parents=[playlist_creator],
    )

    return parser.parse_args(args)


def main():
    args = get_args()

    if args.setup:
        setup()
        sys.exit()

    ytmusic = YTMusicTransfer()
    if args.all:
        s = Spotify()
        pl = s.getUserPlaylists(args.playlist)
        print(str(len(pl)) + " playlists found. Starting transfer...")
        count = 1
        for p in pl:
            print("Playlist " + str(count) + ": " + p["name"])
            count = count + 1
            try:
                playlist = Spotify().getSpotifyPlaylist(p["external_urls"]["spotify"])
                videoIds = ytmusic.search_songs(playlist["tracks"])
                playlist_id = ytmusic.create_playlist(
                    p["name"],
                    p["description"],
                    "PUBLIC" if args.public else "PRIVATE",
                    videoIds,
                )
                print(playlist_id)
            except Exception as ex:
                print(f"Could not transfer playlist {p['name']}. {str(ex)}")
        return

    if args.remove:
        ytmusic.remove_playlists(args.pattern)
        return

    date = ""
    if args.date:
        date = " " + datetime.today().strftime("%m/%d/%Y")
    try:
        playlist = Spotify().getSpotifyPlaylist(args.playlist)
    except Exception as ex:
        print(
            "Could not get Spotify playlist. Please check the playlist link.\n Error: " + repr(ex)
        )
        return

    name = args.name + date if args.name else playlist["name"] + date
    info = playlist["description"] if (args.info is None) else args.info

    if args.update:
        playlistId = ytmusic.get_playlist_id(name)
        videoIds = ytmusic.search_songs(playlist["tracks"])
        ytmusic.remove_songs(playlistId)
        ytmusic.add_playlist_items(playlistId, videoIds)

    else:
        videoIds = ytmusic.search_songs(playlist["tracks"])
        playlistId = ytmusic.create_playlist(
            name, info, "PUBLIC" if args.public else "PRIVATE", videoIds
        )

        print(
            f"Success: created playlist {name}\n"
            f"https://music.youtube.com/playlist?list={playlistId}"
        )


if __name__ == "__main__":
    main()
