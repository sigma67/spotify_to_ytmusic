import argparse
import importlib.metadata
import sys
from pathlib import Path

from spotify_to_ytmusic import controllers


class NewlineVersionAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        sys.stdout.write(
            f"spotify-to-ytmusic {importlib.metadata.version('spotify-to-ytmusic')}\n"
            f"ytmusicapi {importlib.metadata.version('ytmusicapi')} \n"
            f"spotipy {importlib.metadata.version('spotipy')}",
        )
        parser.exit()


def get_args(args=None):
    parser = argparse.ArgumentParser(
        description="Transfer spotify playlists to YouTube Music."
    )
    parser.add_argument(
        "-v",
        "--version",
        nargs=0,
        action=NewlineVersionAction,
    )
    subparsers = parser.add_subparsers(
        help="Provide a subcommand", dest="command", required=True
    )
    setup_parser = subparsers.add_parser("setup", help="Set up credentials")
    setup_parser.set_defaults(func=controllers.setup)
    setup_parser.add_argument(
        "--file", type=Path, help="Optional path to a settings.ini file"
    )

    cache_parser = argparse.ArgumentParser(add_help=False)
    cache_parser.add_argument(
        "--use-cached",
        action="store_true",
        default=False,
        help="(Optional) Enable the use of a cache file to save and retrieve query results.",
    )

    spotify_playlist = argparse.ArgumentParser(add_help=False)
    spotify_playlist.add_argument(
        "playlist", type=str, help="Provide a playlist Spotify link."
    )

    spotify_playlist_create = argparse.ArgumentParser(add_help=False)
    spotify_playlist_create.add_argument(
        "-d",
        "--date",
        action="store_true",
        help="Append the current date to the playlist name",
    )
    spotify_playlist_create.add_argument(
        "-i",
        "--info",
        type=str,
        help="Provide description information for the YouTube Music Playlist. Default: Spotify playlist description",
    )
    spotify_playlist_create.add_argument(
        "-n",
        "--name",
        type=str,
        help="Provide a name for the YouTube Music playlist. Default: Spotify playlist name",
    )
    spotify_playlist_create.add_argument(
        "-p",
        "--public",
        action="store_true",
        help="Make created playlist public. Default: private",
    )
    spotify_playlist_create.add_argument(
        "-l",
        "--like",
        action="store_true",
        help="Like the songs in the specified playlist",
    )

    create_parser = subparsers.add_parser(
        "create",
        help="Create a new playlist on YouTube Music.",
        parents=[spotify_playlist, spotify_playlist_create, cache_parser],
    )
    create_parser.set_defaults(func=controllers.create)

    liked_parser = subparsers.add_parser(
        "liked",
        help="Transfer all liked songs of the user.",
        parents=[spotify_playlist_create, cache_parser],
    )
    liked_parser.set_defaults(func=controllers.liked)

    update_parser = subparsers.add_parser(
        "update",
        help="Delete all entries in the provided Google Play Music playlist and "
        "update the playlist with entries from the Spotify playlist.",
        parents=[spotify_playlist, cache_parser],
    )
    update_parser.set_defaults(func=controllers.update)
    update_parser.add_argument(
        "name", type=str, help="The name of the YouTube Music playlist to update."
    )
    update_parser.add_argument(
        "--append", help="Do not delete items, append to target playlist instead"
    )

    remove_parser = subparsers.add_parser(
        "remove", help="Remove playlists with specified regex pattern."
    )
    remove_parser.set_defaults(func=controllers.remove)
    remove_parser.add_argument("pattern", help="regex pattern")

    all_parser = subparsers.add_parser(
        "all",
        help="Transfer all public playlists of the specified user (Spotify User ID).",
        parents=[cache_parser],
    )
    all_parser.add_argument(
        "user", type=str, help="Spotify userid of the specified user."
    )
    all_parser.set_defaults(func=controllers.all)
    all_parser.add_argument(
        "-l",
        "--like",
        action="store_true",
        help="Like the songs in all of the public playlist",
    )

    search_parser = subparsers.add_parser(
        "search",
        help="Search for a song on YouTube Music to cross-check the algorithm match result.",
        parents=[cache_parser],
    )
    search_parser.add_argument(
        "link", type=str, help="Link of the spotify song to search."
    )
    search_parser.set_defaults(func=controllers.search)

    cache_remove_parser = subparsers.add_parser("cache-clear", help="Clear cache file")
    cache_remove_parser.set_defaults(func=controllers.cache_clear)

    return parser.parse_args(args)


def main():
    args = get_args()
    args.func(args)


if __name__ == "__main__":
    main()
