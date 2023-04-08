import time
import unittest
from io import StringIO
from unittest import mock

from spotify_to_ytmusic.main import get_args, main

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

        with mock.patch("sys.argv", ["", "create", TEST_PLAYLIST, "-n", "test", "-i", "test-playlist", "-d"]):
            main()

        time.sleep(2)
        with mock.patch("sys.argv", ["", "update", TEST_PLAYLIST, "test"]):
            main()

        with mock.patch("sys.argv", ["", "remove", "test"]), mock.patch('sys.stdout', new=StringIO()) as fakeOutput, mock.patch("builtins.input", side_effect="y"):
            main()
            assert int(fakeOutput.getvalue().splitlines()[-1][0]) >= 2
