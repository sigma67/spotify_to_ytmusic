import Setup
import YouTube
import argparse

youtubeHeadersRawFilename = 'youtube_headers_raw.txt'
spotifyPlaylistsFilename = 'spotify_playlists.txt'

def get_parser():
    parser = argparse.ArgumentParser(description='Transfer spotify playlist to YouTube Music.')
    parser.add_argument("-n", "--name", type=str, help="Provide a name for the YouTube Music playlist. Default: Spotify playlist name")
    parser.add_argument("-i", "--info", type=str, help="Provide description information for the YouTube Music Playlist. Default: Spotify playlist description")
    parser.add_argument("-d", "--date", action='store_true', help="Append the current date to the playlist name")
    parser.add_argument("-p", "--public", action='store_true', help="Make the playlist public. Default: private")
    parser.add_argument("-r", "--remove", action='store_true', help="Remove playlists with specified regex pattern.")
    parser.add_argument("-a", "--all", action='store_true', help="Transfer all public playlists of the specified user (Spotify User ID).")
    return parser

def get_args():
    return get_parser().parse_args()

def setup():
    headersRawFile = open(youtubeHeadersRawFilename, 'r')
    setupParser = Setup.get_parser()
    Setup.main(setupParser.parse_args(['--youtube', '--headers_raw', headersRawFile.read()]))
    headersRawFile.close()
    
def get_forwarded_args(url):
    args = get_args()
    forwarded_args = [url]
    forwarded_args += ['-n', args.name] if (args.name is not None) else []
    forwarded_args += ['-i', args.info] if (args.info is not None) else []
    forwarded_args += ['-d'] if (args.date) else []
    forwarded_args += ['-p'] if (args.public) else []
    forwarded_args += ['-r'] if (args.remove) else []
    forwarded_args += ['-a'] if (args.all) else []
    return forwarded_args

def spotify_to_youtube():
    spotifyPlaylistsFile = open(spotifyPlaylistsFilename, 'r')
    playlistUrls = spotifyPlaylistsFile.readlines()
    youtubeParser = YouTube.get_parser()
    for url in playlistUrls:
        stripedUrl = url.strip()
        print('Fetching: ', stripedUrl)
        YouTube.main(youtubeParser.parse_args(get_forwarded_args(stripedUrl)))
    spotifyPlaylistsFile.close()

def main():
    setup()
    spotify_to_youtube()

if __name__ == "__main__":
    main()