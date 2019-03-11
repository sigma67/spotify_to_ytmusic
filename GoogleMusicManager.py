import sys
import os
import settings
from gmusicapi import Musicmanager

path = os.path.dirname(os.path.realpath(__file__)) + '\\'

class GoogleMusicManager:
    def __init__(self):
        self.api = Musicmanager(debug_logging=False)
        with open(path + "oauth.cred", 'w+') as tmp:
            tmp.write(settings['google']['musicmanager'])
            tmp.close()
            self.api.login(tmp.name)
            os.remove(tmp.name)

    def upload_song(self, file):
        self.api.upload(file)


if __name__ == "__main__":
    gmusic = GoogleMusicManager()
    for x in sys.argv[1:]:
        try:
            gmusic.upload_song(x)
            print("Successfully uploaded " + x)
        except Exception as e:
            print("There was an error during the upload for file " + x + ": " + str(e))
