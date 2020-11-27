import argparse
import settings

def get_parser():
    parser = argparse.ArgumentParser(description='Setup Google/Youtube music credentials.')
    parser.add_argument("-mm", "--musicmanager", action='store_true', help="Setup for the google music using MusicManager")
    parser.add_argument("-mc", "--mobileclient", action='store_true', help="Setup for the google music using MobileClient")
    parser.add_argument("-yt", "--youtube", action='store_true', help="Setup for the Youtube Music")
    parser.add_argument("-hr","--headers_raw", type=str, help="Provide header from music.youtube.com/browse")
    return parser

def get_args():
    return get_parser().parse_args()

def main(args):
    if args.mobileclient:
        from gmusicapi import Mobileclient
        api = Mobileclient(debug_logging=True)
        settings['google']['mobileclient'] = api.perform_oauth(open_browser=True).to_json()
    elif args.musicmanager:
        from gmusicapi import Musicmanager
        api = Musicmanager(debug_logging=True)
        settings['google']['musicmanager'] = api.perform_oauth(open_browser=True).to_json()
    elif args.youtube:
        from ytmusicapi import YTMusic
        api = YTMusic()
        settings['youtube']['headers'] = api.setup() if (args.headers_raw is None) else api.setup(headers_raw=args.headers_raw)
    settings.save()

if __name__ == "__main__":
    main(get_args())