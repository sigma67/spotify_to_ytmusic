import sys
from gmusicapi import Musicmanager

credentials = u'./oauth.cred'

class GoogleMusicManager:
    def __init__(self):
        self.api = Musicmanager(debug_logging=False)
        self.api.login(credentials)

    def upload_song(self, file):
        self.api.upload(file)

if __name__ == "__main__":
    if sys.argv[0] == "setup":
        api = Musicmanager(debug_logging=True)
        api.perform_oauth(credentials)
        exit()

    gmusic = GoogleMusicManager()
    gmusic.upload_song(sys.argv[0])
