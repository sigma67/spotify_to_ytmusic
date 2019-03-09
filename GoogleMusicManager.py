import sys
import os
import settings
from gmusicapi import Musicmanager

path = os.path.dirname(os.path.realpath(__file__)) + '\\'

class GoogleMusicManager:
    def __init__(self):
        self.api = Musicmanager(debug_logging=False)
        self.api.login()
        with open(path + "oauth.cred", 'w+') as tmp:
            tmp.write(settings['google']['musicmanager'])
            tmp.close()
            self.api.login(tmp.name)
            os.remove(tmp.name)

    def upload_song(self, file):
        self.api.upload(file)


if __name__ == "__main__":
    gmusic = GoogleMusicManager()
    try:
        gmusic.upload_song(sys.argv[1])
        print("Successfully uploaded " + sys.argv[1])
    except:
        print("There was an error during the upload.")
