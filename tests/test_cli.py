import json
import shutil
import time
import unittest
from io import StringIO
from pathlib import Path
from unittest import mock

from spotify_to_ytmusic.main import get_args, main
from spotify_to_ytmusic.settings import Settings

TEST_PLAYLIST = "https://open.spotify.com/playlist/4UzyZJfSQ4584FaWGwepfL"


class TestCli(unittest.TestCase):
    def test_get_args(self):
        args = get_args(["all", "user"])
        self.assertEqual(len(vars(args)), 3)
        args = get_args(["create", "playlist-link"])
        self.assertEqual(len(vars(args)), 7)
        args = get_args(["update", "playlist-link", "playlist-name"])
        self.assertEqual(len(vars(args)), 5)
        args = get_args(["setup"])
        self.assertEqual(len(vars(args)), 3)

    def test_create(self):
        with mock.patch("sys.argv", ["", "all", "sigmatics"]):
            main()

        with mock.patch(
            "sys.argv", ["", "create", TEST_PLAYLIST, "-n", "spotify_to_ytmusic", "-i", "test-playlist", "-d"]
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
        tmp_path = Path(__file__).parent.joinpath("settings.tmp")
        example_path = Settings.filepath.parent.joinpath("settings.ini.example")
        shutil.copy(example_path, tmp_path)
        with mock.patch("sys.argv", ["", "setup"]), mock.patch(
            "builtins.input", return_value="3"
        ), mock.patch(
            "ytmusicapi.auth.oauth.YTMusicOAuth.get_token_from_code",
            return_value=json.loads(Settings()["youtube"]["headers"]),
        ):
            main()
            assert tmp_path.is_file()
            settings = Settings()
            assert settings["spotify"]["client_id"] == "3"
            assert settings["spotify"]["client_secret"] == "3"
            tmp_path.unlink()

        with mock.patch("sys.argv", ["", "setup", "--file", example_path.as_posix()]), mock.patch(
            "spotify_to_ytmusic.settings.Settings.filepath", tmp_path
        ):
            main()
            assert tmp_path.is_file()
            tmp_path.unlink()
