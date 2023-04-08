import shutil
import sys
from pathlib import Path
from typing import Optional

import ytmusicapi

from spotify_to_ytmusic.settings import Settings


def setup(file: Optional[Path] = None):
    if file:
        setup_file(file)
        return

    choice = input("Choose which API to set up\n" "(1) Spotify\n" "(2) YouTube\n" "(3) both\n")
    choices = ["1", "2", "3"]
    if choice not in choices:
        sys.exit("Invalid choice")

    if choice == choices[0]:
        setup_spotify()
    elif choice == choices[1]:
        setup_youtube()
    elif choice == choices[2]:
        setup_spotify()
        setup_youtube()


def setup_youtube():
    settings = Settings()
    settings["youtube"]["headers"] = ytmusicapi.setup_oauth()
    settings.save()


def setup_spotify():
    settings = Settings()
    credentials = {
        "client_credentials": input(
            "Paste your client credentials from the Spotify developer dashboard:"
        ),
        "client_secrets": input("Paste your client secret from the Spotify developer dashboard:"),
    }
    settings["spotify"].update(credentials)
    settings.save()


def setup_file(file: Path):
    if not file:
        raise FileNotFoundError(f"{file} not found")
    shutil.copy(file, Settings.filepath)
