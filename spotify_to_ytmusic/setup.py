import json
import shutil
import sys
from pathlib import Path
from typing import Optional

import ytmusicapi

from spotify_to_ytmusic.settings import DEFAULT_PATH, EXAMPLE_PATH, Settings
from spotify_to_ytmusic.utils.browser import has_browser


def setup(file: Optional[Path] = None):
    if file:
        shutil.copy(file, DEFAULT_PATH)
        return

    if not DEFAULT_PATH.is_file():
        shutil.copy(EXAMPLE_PATH, DEFAULT_PATH)
    choice = input("Choose which API to set up\n(1) Spotify\n(2) YouTube (oAuth)\n(3) Youtube (Browser)\n(4) both \n")

    choices = ["1", "2", "3", "4"]
    if choice not in choices:
        sys.exit("Invalid choice")

    if choice == choices[0]:
        setup_spotify()
    elif choice == choices[1]:
        setup_youtube()
    elif choice == choices[2]:
        setup_youtube_browser()
    elif choice == choices[3]:
        setup_spotify()
        setup_youtube()


def setup_youtube():
    settings = Settings()
    credentials = ytmusicapi.setup_oauth(open_browser=has_browser())
    settings["youtube"]["headers"] = json.dumps(credentials.as_dict())
    settings["youtube"]["auth_type"] = "oauth"
    settings.save()

def setup_youtube_browser():
    settings = Settings()
    print('Please see https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html for instructions.')
    credentials = ytmusicapi.setup()
    settings["youtube"]["headers"] = credentials
    settings["youtube"]["auth_type"] = "browser"
    settings.save()


def setup_spotify():
    settings = Settings()
    credentials = {
        "client_id": input("Paste your client id from the Spotify developer dashboard:"),
        "client_secret": input("Paste your client secret from the Spotify developer dashboard:"),
        "use_oauth": input(
            "Use OAuth method for authorization to transfer private playlists (yes/no):"
        ),
    }
    settings["spotify"].update(credentials)
    settings.save()
