import argparse
import sys
from datetime import datetime

from spotify_to_ytmusic.Setup import setup
from spotify_to_ytmusic.SpotifyExport import Spotify
from spotify_to_ytmusic.YouTube import YTMusicTransfer


def get_args():
    parser = argparse.ArgumentParser(description='Transfer spotify playlist to YouTube Music.')
    parser.add_argument("playlist", type=str, help="Provide a playlist Spotify link.")
    parser.add_argument("-u", "--update", action='store_true', help="Delete all entries in the provided Google Play Music playlist and update the playlist with entries from the Spotify playlist.")
    parser.add_argument("-n", "--name", type=str, help="Provide a name for the YouTube Music playlist. Default: Spotify playlist name")
    parser.add_argument("-i", "--info", type=str, help="Provide description information for the YouTube Music Playlist. Default: Spotify playlist description")
    parser.add_argument("-d", "--date", action='store_true', help="Append the current date to the playlist name")
    parser.add_argument("-p", "--public", action='store_true', help="Make the playlist public. Default: private")
    parser.add_argument("-r", "--remove", action='store_true', help="Remove playlists with specified regex pattern.")
    parser.add_argument("-a", "--all", action='store_true', help="Transfer all public playlists of the specified user (Spotify User ID).")
    parser.add_argument("--setup", help="Set up credentials")
    return parser.parse_args()


def main():
    args = get_args()
    ytmusic = YTMusicTransfer()

    if args.setup:
        setup()
        sys.exit()

    if args.all:
        s = Spotify()
        pl = s.getUserPlaylists(args.playlist)
        print(str(len(pl)) + " playlists found. Starting transfer...")
        count = 1
        for p in pl:
            print("Playlist " + str(count) + ": " + p['name'])
            count = count + 1
            try:
                playlist = Spotify().getSpotifyPlaylist(p['external_urls']['spotify'])
                videoIds = ytmusic.search_songs(playlist['tracks'])
                playlist_id = ytmusic.create_playlist(p['name'], p['description'],
                                                    'PUBLIC' if args.public else 'PRIVATE',
                                                    videoIds)
                print(playlist_id)
            except Exception as ex:
                print("Could not transfer playlist " + p['name'] + ". Exception" + str(ex))
        return

    if args.remove:
        ytmusic.remove_playlists(args.playlist)
        return

    date = ""
    if args.date:
        date = " " + datetime.today().strftime('%m/%d/%Y')
    try:
        playlist = Spotify().getSpotifyPlaylist(args.playlist)
    except Exception as ex:
        print("Could not get Spotify playlist. Please check the playlist link.\n Error: " + repr(ex))
        return

    name = args.name + date if args.name else playlist['name'] + date
    info = playlist['description'] if (args.info is None) else args.info

    if args.update:
        playlistId = ytmusic.get_playlist_id(name)
        videoIds = ytmusic.search_songs(playlist['tracks'])
        ytmusic.remove_songs(playlistId)
        ytmusic.add_playlist_items(playlistId, videoIds)

    else:
        videoIds = ytmusic.search_songs(playlist['tracks'])
        playlistId = ytmusic.create_playlist(name, info, 'PUBLIC' if args.public else 'PRIVATE', videoIds)

        print("Success: created playlist \"" + name + "\"\n" +
              "https://music.youtube.com/playlist?list=" + playlistId)


if __name__ == "__main__":
    main()
