import sys
import settings
from gmusicapi import Musicmanager, Mobileclient
from YouTube import YouService
import os
import json

if __name__ == "__main__":

    if sys.argv[1] == "mobileclient":
        api = Mobileclient(debug_logging=True)
        settings['google']['mobileclient'] = api.perform_oauth(open_browser=True).to_json()

    elif sys.argv[1] == "musicmanager":
        api = Musicmanager(debug_logging=True)
        settings['google']['musicmanager'] = api.perform_oauth(open_browser=True).to_json()

    elif sys.argv[1] == "youtube":
        path = os.path.dirname(os.path.realpath(__file__)) + os.sep
        tmp = open(path + "oauth.cred", 'w+')
        tmp.write(settings['youtube']['client_secrets'])
        tmp.close()
        credentials = YouService.authorize(tmp.name)
        os.remove(tmp.name)

        data = dict(
            refresh_token=credentials.refresh_token,
            token_uri=credentials.token_uri,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
            scopes=credentials.scopes,
        )
        settings['youtube']['credentials'] = json.dumps(data)

    settings.save()