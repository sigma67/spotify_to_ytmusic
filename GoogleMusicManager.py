import sys
import settings
from gmusicapi import Musicmanager

class GoogleMusicManager:
    def __init__(self):
        self.api = Musicmanager(debug_logging=False)
        self.api.login(settings['google']['musicmanager'])

    def upload_song(self, file):
        self.api.upload(file)

if __name__ == "__main__":
    gmusic = GoogleMusicManager()
    gmusic.upload_song(sys.argv[0])
