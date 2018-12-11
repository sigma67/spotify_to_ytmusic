import sys
import os
import settings
from gmusicapi import Musicmanager


class GoogleMusicManager:
    def __init__(self):
        self.api = Musicmanager(debug_logging=False)
        self.api.login()
        with open(os.path.dirname(os.path.realpath(__file__)) + "oauth.cred", 'w+') as tmp:
            tmp.write(settings['google']['musicmanager'])
            tmp.close()
            self.api.login(tmp.name)
            os.remove(tmp.name)

    def upload_song(self, file):
        self.api.upload(file)


if __name__ == "__main__":
    gmusic = GoogleMusicManager()
    gmusic.upload_song(sys.argv[0])
