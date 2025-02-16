import argparse
import sys
from pathlib import Path

from spotify_to_ytmusic import controllers
import importlib.metadata


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
        parents=[spotify_playlist, spotify_playlist_create, get_common_extended_args()],
    )
    create_parser.set_defaults(func=controllers.create)

    liked_parser = subparsers.add_parser(
        "liked",
        help="Transfer all liked songs of the user.",
        parents=[spotify_playlist_create, get_common_extended_args()],
    )
    liked_parser.set_defaults(func=controllers.liked)

    update_parser = subparsers.add_parser(
        "update",
        help="Update a YouTube Music playlist with entries from Spotify. To update liked songs from Spotify, just include 'liked' in playlist argument.",
        parents=[spotify_playlist, get_common_extended_args()],
    )
    update_parser.set_defaults(func=controllers.update)
    update_parser.add_argument("name", type=str, help="The name of the YouTube Music playlist to update.")
    update_parser.add_argument("--append", action="store_true", help="Do not delete items, append to target playlist instead.")
    update_parser.add_argument("--reset", action="store_true", help="Delete all items then re-add to target playlist. (Note: If playlist is big, the request can get timed out.)")

    remove_parser = subparsers.add_parser("remove", help="Remove playlists with specified regex pattern.")
    remove_parser.set_defaults(func=controllers.remove)
    remove_parser.add_argument("pattern", help="Regex pattern")

    # All command (common arguments included)
    all_parser = subparsers.add_parser(
        "all",
        help="Transfer all public playlists of the specified user (Spotify User ID).",
        parents=[get_common_extended_args()],
    )
    all_parser.add_argument("user", type=str, help="Spotify user ID of the specified user.")
    all_parser.set_defaults(func=controllers.all)
    all_parser.add_argument(
        "-l",
        "--like",
        action="store_true",
        help="Like the songs in all of the public playlists",
    )

    search_parser = subparsers.add_parser("search", help="Search for a song in YT Music.", parents=[get_common_extended_args()])
    search_parser.set_defaults(func=controllers.search)
    search_parser.add_argument("link", type=str, help="Link of the Spotify song to search.")

    cache_clear_parser = subparsers.add_parser("cache-clear", help="Clear cache file")
    cache_clear_parser.set_defaults(func=controllers.cache_clear)

    fix_match_parser = subparsers.add_parser("fix-match", help="Fix an incorrect match by YouTube Music ID")
    fix_match_parser.set_defaults(func=controllers.fix_match)
    fix_match_parser.add_argument("--current-id", type=str, help="The existing YouTube Music ID of the song to be fixed")
    fix_match_parser.add_argument("--new-id", type=str, help="The new YouTube Music ID to replace the existing one")


    return parser.parse_args(args)

def get_common_extended_args():
    """Creates a parser with common optional arguments."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--extended-search",
        action="store_true",
        help="Use new algorithm for searching track on YouTube Music (beta).",
    )
    parser.add_argument(
        '--confidence',
        type=float,
        nargs='?',
        default=None,
        help="(Optional) How strict algorithm match should be (0-1 ONLY)",
    )
    parser.add_argument(
        '--use-cached',
        action="store_true",
        default=False,
        help="(Optional) Enable the use of a cache file to save and retrieve query results.",
    )
    parser.add_argument(
        '--search-albums',
        action="store_true",
        default=False,
        help="(Optional) Search songs in albums (Note: This makes search really slow).",
    )
    parser.add_argument(
        '--enable-fallback',
        action="store_true",
        default=False,
        help="(Optional) Enable fallback to default search algorithm if confidence threshold doesn't match any results.",
    )
    return parser

def main():
    args = get_args()
    args.func(args)


if __name__ == "__main__":
    main()
