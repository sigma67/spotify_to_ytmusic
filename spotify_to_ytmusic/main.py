import argparse
from pathlib import Path

from spotify_to_ytmusic import controllers


def get_args(args=None):
    parser = argparse.ArgumentParser(description="Transfer spotify playlists to YouTube Music.")

    subparsers = parser.add_subparsers(help="Provide a subcommand", dest="command", required=True)
    setup_parser = subparsers.add_parser("setup", help="Set up credentials")
    setup_parser.set_defaults(func=controllers.setup)
    setup_parser.add_argument("--file", type=Path, help="Optional path to a settings.ini file")

    spotify_playlist = argparse.ArgumentParser(add_help=False)
    spotify_playlist.add_argument("playlist", type=str, help="Provide a playlist Spotify link.")

    create_parser = subparsers.add_parser(
        "create",
        help="Create a new playlist on YouTube Music.",
        parents=[spotify_playlist],
    )
    create_parser.set_defaults(func=controllers.create)
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
    create_parser.add_argument(
        "-p",
        "--public",
        action="store_true",
        help="Make created playlist public. Default: private",
    )

    update_parser = subparsers.add_parser(
        "update",
        help="Delete all entries in the provided Google Play Music playlist and update the playlist with entries from the Spotify playlist.",
        parents=[spotify_playlist],
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
        "all", help="Transfer all public playlists of the specified user (Spotify User ID)."
    )
    all_parser.add_argument("user", type=str, help="Spotify userid of the specified user.")
    all_parser.set_defaults(func=controllers.all)

    return parser.parse_args(args)


def main():
    args = get_args()
    args.func(args)


if __name__ == "__main__":
    main()
