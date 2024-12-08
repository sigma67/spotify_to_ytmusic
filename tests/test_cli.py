import json
import os
import time
import unittest
import tempfile
from io import StringIO
from unittest import mock

from spotify_to_ytmusic import controllers, settings as settings_module
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
        self.assertEqual(len(vars(args)), 9)
        args = get_args(["create", "playlist-link"])
        self.assertEqual(len(vars(args)), 13)
        args = get_args(["update", "playlist-link", "playlist-name"])
        self.assertEqual(len(vars(args)), 10)
        args = get_args(["setup"])
        self.assertEqual(len(vars(args)), 3)

        args = get_args(["create", TEST_PLAYLIST, "--extended-search", "--confidence", "0.7", "--use-cached"])
        self.assertTrue(args.extended_search)
        self.assertEqual(args.confidence, 0.7)
        self.assertTrue(args.use_cached)

        args = get_args(["create", TEST_PLAYLIST, "--search-albums", "--enable-fallback"])
        self.assertTrue(args.search_albums)
        self.assertTrue(args.enable_fallback)

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

    def test_create_with_extended_search(self):
        with mock.patch(
            "sys.argv",
            [
                "",
                "create",
                TEST_PLAYLIST,
                "--extended-search",
                "--confidence",
                "0.7",
                "--use-cached",
                "--search-albums",
            ],
        ), mock.patch("sys.stdout", new=StringIO()) as fake_output:
            main()
            output = fake_output.getvalue()
            self.assertIn("Success: created playlist", output)

    def test_create_with_extended_search_and_cached(self):
        with mock.patch(
            "sys.argv",
            [
                "",
                "create",
                TEST_PLAYLIST,
                "--extended-search",
                "--confidence",
                "0.7",  
                "--use-cached",
                "--search-albums",
            ],
        ), mock.patch("sys.stdout", new=StringIO()) as fake_output:
            main()
            output = fake_output.getvalue()
            self.assertIn("Found cached link from lookup table", output)
    
    def test_fix_match(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            lookup_path = os.path.join(temp_dir, "lookup.json")
            test_data = {
                "Stefano Crabuzza Let It Go": "R8M57jVEjGU",
                "Stefano Noferini Dance U": "oXGhDY9OWJ0",
            }
        
            with open(lookup_path, "w") as f:
                json.dump(test_data, f, indent=4)
        
            class MockArgs:
                def __init__(self, current_id, new_id):
                    self.current_id = current_id
                    self.new_id = new_id
                    self.func = mock.Mock(side_effect=controllers.fix_match)
        
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
                mock.patch('os.path.dirname', return_value=temp_dir), \
                mock.patch('os.path.realpath', return_value=temp_dir), \
                mock.patch('os.path.exists', return_value=True), \
                mock.patch('sys.argv', ["", "fix-match", "R8M57jVEjGU", "oXGhDY9OWJ0"]):  # Kept as is
            
                with mock.patch('argparse.ArgumentParser.parse_args',
                                return_value=MockArgs("R8M57jVEjGU", "oXGhDY9OWJ0")):  # Updated to match
                    main()
                output = mock_stdout.getvalue().strip()
                # print(f"DEBUG: Captured Output -> {output}")
            
                self.assertIn("Replacing R8M57jVEjGU with oXGhDY9OWJ0", output)
            
                with open(lookup_path, "r") as f:
                    updated_data = json.load(f)
            
                self.assertEqual(updated_data["Stefano Crabuzza Let It Go"], "oXGhDY9OWJ0")

    def test_cache_clear(self):
        test_dir = os.path.dirname(os.path.realpath(__file__))

        potential_paths = [
            os.path.join(os.path.dirname(test_dir), "spotify_to_ytmusic", "lookup.json")
        ]
        
        with mock.patch("sys.argv", ["", "cache-clear"]), \
            mock.patch.object(controllers, "cache_clear", wraps=controllers.cache_clear) as mock_clear, \
            mock.patch("os.remove") as mock_remove, \
            mock.patch("os.path.exists", return_value=True):

            main()

            for call in mock_remove.call_args_list:
                print(call)

            mock_clear.assert_called_once()
            
            remove_calls = mock_remove.call_args_list
            if not remove_calls:
                self.fail("os.remove was not called")
            
            actual_path = remove_calls[0][0][0]
            self.assertIn(actual_path, potential_paths, 
                f"Unexpected path: {actual_path}. Expected one of {potential_paths}")
        
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
