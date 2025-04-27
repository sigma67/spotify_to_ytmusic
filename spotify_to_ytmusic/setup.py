import json
import shutil
import sys
from pathlib import Path

import ytmusicapi
from charset_normalizer.cli import query_yes_no

import spotify_to_ytmusic.settings as settings_module
from spotify_to_ytmusic.settings import (
    DEFAULT_PATH,
    EXAMPLE_PATH,
    Settings,
)
from spotify_to_ytmusic.utils.browser import has_browser


def setup(file: Path | None = None):
    if file:
        shutil.copy(file, DEFAULT_PATH)
        return

    if not DEFAULT_PATH.is_file():
        shutil.copy(EXAMPLE_PATH, DEFAULT_PATH)
    choice = input(
        "Choose which API to set up\n(1) Spotify\n(2) Youtube (Browser)(recommended)\n(3) YouTube (oAuth)"
        "\n(4) both (Spotify + YouTube (oAuth)\n"
    )

    choices = ["1", "2", "3", "4"]
    if choice not in choices:
        sys.exit("Invalid choice")

    if choice == choices[0]:
        setup_spotify()
    elif choice == choices[1]:
        setup_youtube_browser()
    elif choice == choices[2]:
        setup_youtube()
    elif choice == choices[3]:
        setup_youtube()
        setup_spotify()


def setup_youtube():
    settings = Settings()
    credentials = {
        "client_id": input(
            "Paste your client id from the Google Cloud YouTube API here:"
        ),
        "client_secret": input(
            "Paste your client secret from the Google Cloud YouTube API here:"
        ),
    }
    headers = ytmusicapi.setup_oauth(
        client_id=credentials["client_id"],
        client_secret=credentials["client_secret"],
        open_browser=has_browser(),
    )
    settings["youtube"].update(
        {
            "headers": json.dumps(headers.as_dict()),
            "auth_type": "oauth",
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
        },
    )
    settings.save()


def setup_youtube_browser():
    settings = Settings()
    print(
        "Please see https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html for instructions."
    )
    credentials = ytmusicapi.setup()
    settings["youtube"]["headers"] = credentials
    settings["youtube"]["auth_type"] = "browser"
    settings.save()


def setup_spotify():
    settings = Settings()
    credentials = {
        "client_id": input(
            "Paste your client id from the Spotify developer dashboard:"
        ),
        "client_secret": input(
            "Paste your client secret from the Spotify developer dashboard:"
        ),
        "use_oauth": str(
            query_yes_no(
                "Use OAuth method for authorization to transfer private playlists:"
            )
        ),
    }
    settings["spotify"].update(credentials)

    # remove Spotipy cache file to prevent issues when a second account is set up
    settings_module.SPOTIPY_CACHE_FILE.unlink(missing_ok=True)

    settings.save()
