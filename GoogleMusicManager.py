import sys
import os
import json
import settings
from gmusicapi import session, Musicmanager

path = os.path.dirname(os.path.realpath(__file__)) + os.sep

class GoogleMusicManager:
    def __init__(self):
        self.api = Musicmanager(debug_logging=False)
        refresh_token = json.loads(settings['google']['musicmanager'])['refresh_token']
        credentials = session.credentials_from_refresh_token(refresh_token, session.Mobileclient.oauth)
        self.api.login(credentials)

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
