import sys
import settings

if __name__ == "__main__":
    if sys.argv[1] == "youtube":
        from ytmusicapi import YTMusic
        api = YTMusic()
        settings['youtube']['headers'] = api.setup()
    settings.save()