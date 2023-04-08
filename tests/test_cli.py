import unittest

from spotify_to_ytmusic.main import get_args


class TestCli(unittest.TestCase):
    def test_get_args(self):
        args = get_args(["all", "--public", "user"])
        self.assertEqual(len(vars(args)), 3)
        args = get_args(["create", "playlist-link"])
        self.assertEqual(len(vars(args)), 7)
        args = get_args(["update", "playlist-link"])
        self.assertEqual(len(vars(args)), 4)
        args = get_args(["setup"])
        self.assertEqual(len(vars(args)), 3)
