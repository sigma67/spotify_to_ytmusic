import json
import time
import unittest
from io import StringIO
from unittest import mock

from spotify_to_ytmusic import settings as settings_module
from spotify_to_ytmusic import setup
from spotify_to_ytmusic.main import get_args, main
from spotify_to_ytmusic.settings import DEFAULT_PATH, EXAMPLE_PATH, Settings

TEST_PLAYLIST = "https://open.spotify.com/playlist/4UzyZJfSQ4584FaWGwepfL"


class TestCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Settings()

    def test_get_args(self):
        args = get_args(["all", "user"])
        self.assertEqual(len(vars(args)), 3)
        args = get_args(["create", "playlist-link"])
        self.assertEqual(len(vars(args)), 7)
        args = get_args(["update", "playlist-link", "playlist-name"])
        self.assertEqual(len(vars(args)), 5)
        args = get_args(["setup"])
        self.assertEqual(len(vars(args)), 3)

    def test_liked(self):
        with mock.patch(
            "sys.argv", ["", "liked", "-n", "spotify_to_ytmusic", "-d", "-i", "test liked"]
        ):
            main()

    def test_create(self):
        with mock.patch("sys.argv", ["", "all", "sigmatics"]):
            main()

        with mock.patch(
            "sys.argv",
            ["", "create", TEST_PLAYLIST, "-n", "spotify_to_ytmusic", "-i", "test-playlist", "-d"],
        ):
            main()

        time.sleep(2)
        with mock.patch("sys.argv", ["", "update", TEST_PLAYLIST, "spotify_to_ytmusic"]):
            main()

        time.sleep(2)
        with mock.patch("sys.argv", ["", "remove", "spotify\_to\_ytmusic"]), mock.patch(
            "sys.stdout", new=StringIO()
        ) as fakeOutput, mock.patch("builtins.input", side_effect="y"):
            main()
            assert (
                int(fakeOutput.getvalue().splitlines()[-1][0]) >= 2
            )  # assert number of lines deleted

    def test_setup(self):
        tmp_path = DEFAULT_PATH.with_suffix(".tmp")
        with (
            mock.patch("sys.argv", ["", "setup"]),
            mock.patch("builtins.input", side_effect=["4", "a", "b", "yes", ""]),
            mock.patch(
                "ytmusicapi.auth.oauth.credentials.OAuthCredentials.token_from_code",
                return_value=json.loads(Settings()["youtube"]["headers"]),
            ),
            mock.patch.object(setup, "DEFAULT_PATH", tmp_path),
            mock.patch("spotify_to_ytmusic.setup.has_browser", return_value=False),
            mock.patch.object(settings_module, "DEFAULT_PATH", tmp_path),
            mock.patch.object(Settings, "filepath", tmp_path),
        ):
            main()
            assert tmp_path.is_file()
            settings = Settings()  # reload settings
            assert settings["spotify"]["client_id"] == "a"
            assert settings["spotify"]["client_secret"] == "b"
            tmp_path.unlink()

        with (
            mock.patch("sys.argv", ["", "setup", "--file", EXAMPLE_PATH.as_posix()]),
            mock.patch.object(setup, "DEFAULT_PATH", tmp_path),
            mock.patch.object(settings_module, "DEFAULT_PATH", tmp_path),
        ):
            main()
            assert tmp_path.is_file()
            tmp_path.unlink()
