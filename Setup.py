import sys
import settings

if __name__ == "__main__":
    if sys.argv[1] == "mobileclient":
        from gmusicapi import Mobileclient
        api = Mobileclient(debug_logging=True)
        settings['google']['mobileclient'] = api.perform_oauth(open_browser=True).to_json()
    elif sys.argv[1] == "musicmanager":
        from gmusicapi import Musicmanager
        api = Musicmanager(debug_logging=True)
        settings['google']['musicmanager'] = api.perform_oauth(open_browser=True).to_json()
    elif sys.argv[1] == "youtube":
        from ytmusicapi import YTMusic
        api = YTMusic()
        settings['youtube']['headers'] = api.setup()
    settings.save()