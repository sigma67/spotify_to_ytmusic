import unittest
from pathlib import Path
from platformdirs import user_cache_dir
from spotify_to_ytmusic.utils.cache_manager import CacheManager


class TestCacheManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cache_manager = CacheManager()
        cls.test_data = {
            "Jordan Burns Weekend": "4ga4xy7omAE",
            "Robert DeLong Lights LŪN Did It To Myself - LŪN Remix": "M7jON1NmyoY",
        }

    def setUp(self):
        self.cache_manager.remove_cache_file()

    def test_save_and_load_lookup_table(self):
        """Test that data is correctly saved and loaded from cache."""
        self.cache_manager.save_to_lookup_table(self.test_data)

        loaded_data = self.cache_manager.load_lookup_table()
        self.assertEqual(loaded_data, self.test_data)

    def test_load_empty_lookup_table(self):
        """Test that loading a non-existing cache returns an empty dictionary."""
        self.assertEqual(self.cache_manager.load_lookup_table(), {})

    def test_remove_cache_file(self):
        """Test that the cache file is properly deleted."""
        self.cache_manager.save_to_lookup_table(self.test_data)

        self.assertTrue(self.cache_manager.cache_file.exists())

        self.cache_manager.remove_cache_file()
        self.assertFalse(self.cache_manager.cache_file.exists())

    def test_cache_file_location(self):
        """Test that the cache file is created in the correct platformdirs location."""
        expected_path = (
            Path(user_cache_dir(appname="spotify_to_ytmusic", appauthor=False))
            / "lookup.json"
        )
        self.assertEqual(self.cache_manager.cache_file, expected_path)


if __name__ == "__main__":
    unittest.main()
