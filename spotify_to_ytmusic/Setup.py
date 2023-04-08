import sys

import ytmusicapi

from spotify_to_ytmusic.settings import Settings

settings = Settings()


def setup():
    choice = input(
        "Choose which API to set up\n" "(1) Spotify\n" "(2) YouTube\n" "(3) both"
    )
    choices = ["1", "2", "3"]
    if choice not in choices:
        sys.exit("Invalid choice")

    if choice == choices[0]:
        setup_spotify()
    elif choice == choices[1]:
        setup_youtube()
    else:
        setup_spotify()
        setup_youtube()


def setup_youtube():
    settings["youtube"]["headers"] = ytmusicapi.setup_oauth()
    settings.save()


def setup_spotify():
    pass
    # settings['spotipy']
