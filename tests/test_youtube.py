import unittest
from spotify_to_ytmusic.ytmusic import YTMusicTransfer


class TestYTMusic(unittest.TestCase):
    def setUp(self):
        self.ytmusic = YTMusicTransfer()
        self.playlist_name = "spotify_to_ytmusic"
        self.playlistId = self.ytmusic.get_playlist_id(self.playlist_name)

    def test_get_playlist_videoIds(self):
        """Test retrieving video IDs from a YouTube Music playlist."""
        video_ids = self.ytmusic.get_playlist_videoIds(self.playlistId)
        print("Fetched video IDs:", video_ids)
        self.assertIsInstance(video_ids, list)
        if video_ids:
            self.assertIsInstance(video_ids[0], str)

    def test_remove_specified_tracks(self):
        """Test removing two tracks from a YouTube Music playlist."""
        video_ids = self.ytmusic.get_playlist_videoIds(self.playlistId)
        print("Before Removal:", video_ids)

        if len(video_ids) < 2:
            self.skipTest("Not enough tracks in the playlist to test removal.")

        tracks_to_remove = video_ids[:2]  # Remove first 2 tracks
        self.ytmusic.remove_specified_tracks(self.playlistId, tracks_to_remove)

        updated_video_ids = self.ytmusic.get_playlist_videoIds(self.playlistId)
        print("After Removal:", updated_video_ids)

        for track in tracks_to_remove:
            self.assertNotIn(track, updated_video_ids)


if __name__ == "__main__":
    unittest.main()
