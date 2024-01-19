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
    choice = input("Choose which API to set up\n" "(1) Spotify\n" "(2) YouTube\n" "(3) both\n" "(4) reddit\n")
    choices = ["1", "2", "3", "4"]
    if choice not in choices:
        sys.exit("Invalid choice")

    if choice == choices[0]:
        setup_spotify()
    elif choice == choices[1]:
        setup_youtube()
    elif choice == choices[2]:
        setup_spotify()
        setup_youtube()
    elif choice == choices[3]:
        setup_reddit()


def setup_youtube():
    settings = Settings()
    credentials = ytmusicapi.setup_oauth(open_browser=has_browser())
    settings["youtube"]["headers"] = json.dumps(credentials.as_dict())
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


def setup_reddit():
    import socket

    def receive_connection():
        """Wait for and then return a connected socket..

        Opens a TCP connection on port 8080, and waits for a single client.

        """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("localhost", 8080))
        server.listen(1)
        client = server.accept()[0]
        server.close()
        return client

    import praw
    agent = 'ytmusic playlist app by /u/Sigmatics'

    settings = Settings()
    reddit = praw.Reddit(client_id=settings['reddit']['client_id'],
                         client_secret=settings['reddit']['client_secret'],
                         redirect_uri='http://localhost:8080',
                         user_agent=agent)

    print(reddit.auth.url(['identity', 'read', 'submit'], '322', 'permanent'))

    client = receive_connection()
    data = client.recv(1024).decode("utf-8")
    param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
    params = {
        key: value
        for (key, value) in [token.split("=") for token in param_tokens]
    }
    settings['reddit']['refresh_token'] = reddit.auth.authorize(params["code"])

    settings.save()
