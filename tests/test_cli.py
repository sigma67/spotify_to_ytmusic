import json
import time
from io import StringIO
from pathlib import Path
from unittest import mock

import pytest

from spotify_to_ytmusic import settings as settings_module
from spotify_to_ytmusic import setup
from spotify_to_ytmusic.main import get_args, main
from spotify_to_ytmusic.settings import CACHE_DIR, DEFAULT_PATH, EXAMPLE_PATH, Settings

TEST_PLAYLIST = "https://open.spotify.com/playlist/4UzyZJfSQ4584FaWGwepfL"
TEST_SONG = "https://open.spotify.com/track/7bnczC5ATlZaZX0MHjX7KU?si=5a07bffaf6324717"


class TestCli:
    @pytest.fixture(autouse=True)
    def fixture_settings(self):
        Settings()

    def test_get_args(self):
        args = get_args(["all", "user"])
        assert len(vars(args)) == 6
        args = get_args(["create", "playlist-link"])
        assert len(vars(args)) == 10
        args = get_args(["update", "playlist-link", "playlist-name"])
        assert len(vars(args)) == 7
        args = get_args(["liked"])
        assert len(vars(args)) == 9
        args = get_args(["search", "link"])
        assert len(vars(args)) == 5
        args = get_args(["setup"])
        assert len(vars(args)) == 4

    def test_liked(self):
        with mock.patch(
            "sys.argv",
            ["", "liked", "-n", "spotify_to_ytmusic", "-d", "-i", "test liked"],
        ):
            main()

    def test_create(self):
        with mock.patch("sys.argv", ["", "all", "sigmatics"]):
            main()

        with mock.patch(
            "sys.argv",
            [
                "",
                "create",
                TEST_PLAYLIST,
                "-n",
                "spotify_to_ytmusic",
                "-i",
                "test-playlist",
                "-d",
            ],
        ):
            main()

        time.sleep(2)
        with mock.patch(
            "sys.argv", ["", "update", TEST_PLAYLIST, "spotify_to_ytmusic"]
        ):
            main()

        time.sleep(2)
        with (
            mock.patch("sys.argv", ["", "remove", r"spotify\_to\_ytmusic"]),
            mock.patch("sys.stdout", new=StringIO()) as fakeOutput,
            mock.patch("builtins.input", side_effect="y"),
        ):
            main()
            assert (
                int(fakeOutput.getvalue().splitlines()[-1][0]) >= 2
            )  # assert number of lines deleted

    def test_search(self):
        with mock.patch("sys.argv", ["", "search", TEST_SONG]):
            main()

    def test_search_with_use_cached_flag(self):
        cache_file = CACHE_DIR / "lookup.json"

        # Ensure the cache file doesn't exist before running the test
        if cache_file.exists():
            cache_file.unlink()

        with mock.patch("sys.argv", ["", "search", TEST_SONG, "--use-cached"]):
            main()
        assert cache_file.exists(), "Cache file was not created."

    def test_setup(self):
        tmp_path = DEFAULT_PATH.with_suffix(".tmp")
        settings = Settings()
        with (
            mock.patch("sys.argv", ["", "setup"]),
            mock.patch(
                "builtins.input",
                side_effect=[
                    "4",
                    settings["youtube"]["client_id"],
                    settings["youtube"]["client_secret"],
                    "yes",
                    "a",
                    "b",
                    "",
                ],
            ),
            mock.patch(
                "ytmusicapi.auth.oauth.credentials.OAuthCredentials.token_from_code",
                return_value=json.loads(settings["youtube"]["headers"]),
            ),
            mock.patch.object(setup, "DEFAULT_PATH", tmp_path),
            mock.patch("spotify_to_ytmusic.setup.has_browser", return_value=False),
            mock.patch.object(settings_module, "DEFAULT_PATH", tmp_path),
            mock.patch.object(settings_module, "SPOTIPY_CACHE_FILE", Path("notexist")),
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
            mock.patch.object(settings_module, "SPOTIPY_CACHE_FILE", Path("notexist")),
            mock.patch.object(settings_module, "DEFAULT_PATH", tmp_path),
        ):
            main()
            assert tmp_path.is_file()
            tmp_path.unlink()
