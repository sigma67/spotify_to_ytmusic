import sys
import settings
from gmusicapi import Musicmanager, Mobileclient

if __name__ == "__main__":
    if sys.argv[1] == "mobileclient":
        api = Mobileclient(debug_logging=True)
        settings['google']['mobileclient'] = api.perform_oauth(open_browser=True).to_json()
    elif sys.argv[1] == "musicmanager":
        api = Musicmanager(debug_logging=True)
        settings['google']['musicmanager'] = api.perform_oauth(open_browser=True).to_json()
    settings.save()