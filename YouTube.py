from ytmusicapi import YTMusic
from datetime import datetime
import os
import argparse
import difflib
from SpotifyExport import Spotify

path = os.path.dirname(os.path.realpath(__file__)) + os.sep


class YTMusicTransfer:
    def __init__(self):
        self.api = YTMusic('headers_auth.json')

    def create_playlist(self, name, info, privacy="PRIVATE"):
        return self.api.create_playlist(name, info, privacy)

    def get_best_fit_song_id(self, results, song):
        match_score = {}
        for res in results:
            compare = res['artist'] + ' ' + res['title']
            match_score[res['videoId']] = difflib.SequenceMatcher(a=song.lower(), b=compare.lower()).ratio()

        return max(match_score, key=match_score.get)

    def search_songs(self, tracks):
        videoIds = []
        songs = list(tracks)
        notFound = list()
        for i, song in enumerate(songs):
            song = song.replace(" &", "")
            result = self.api.search(song)
            if len(result) == 0:
                notFound.append(song)
            else:
                videoIds.append(self.get_best_fit_song_id(result, song))
            if i % 10 == 0:
                print(str(i) + ' searched')

        return videoIds, notFound

    def add_songs(self, playlist, tracks):
        videoIds, notFound = self.search_songs(tracks)

        for videoId in videoIds:
            self.api.add_playlist_item(playlist, videoId)

        with open(path + 'noresults_youtube.txt', 'w', encoding="utf-8") as f:
            f.write("\n".join(notFound))
            f.close()


def get_args():
    parser = argparse.ArgumentParser(description='Transfer spotify playlist to YouTube Music.')
    parser.add_argument("playlist", type=str, help="Provide a playlist Spotify link. Alternatively, provide a text file (one song per line)")
   #parser.add_argument("-u", "--update", type=str, help="Delete all entries in the provided Google Play Music playlist and update the playlist with entries from the Spotify playlist.")
    parser.add_argument("-n", "--name", type=str, help="Provide a name for the YouTube Music playlist. Default: Spotify playlist name")
    parser.add_argument("-i", "--info", type=str, help="Provide description information for the YouTube Music Playlist. Default: Spotify playlist description")
    parser.add_argument("-d", "--date", action='store_true', help="Append the current date to the playlist name")
    parser.add_argument("-p", "--public", action='store_true', help="Make the playlist public. Default: private")
    #parser.add_argument("-r", "--remove", action='store_true', help="Remove playlists with specified regex pattern.")
    #parser.add_argument("-a", "--all", action='store_true', help="Transfer all public playlists of the specified user (Spotify User ID).")
    return parser.parse_args()


def main():
    args = get_args()
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
    ytmusic = YTMusicTransfer()
    playlistId = ytmusic.create_playlist(name, info, 'PUBLIC' if args.public else 'PRIVATE')
    ytmusic.add_songs(playlistId, playlist['tracks'])

    comment = "[YouTube Music](https://music.youtube.com/playlist?list=" + playlistId + ")"
    with open(path + "comment.txt", 'a') as f:
        f.write(comment + '\n\n')

    print("Success: created playlist \"" + name + "\"")


if __name__ == "__main__":
    main()