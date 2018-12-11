from gmusicapi import Mobileclient
from SpotifyExport import Spotify
import sys
import os
import re
import difflib
import settings
import argparse
from datetime import datetime

path = os.path.dirname(os.path.realpath(__file__))


class GoogleMusic:
    def __init__(self):
        self.api = Mobileclient(debug_logging=False)
        with open(path + "oauth.cred", 'w+') as tmp:
            tmp.write(settings['google']['mobileclient'])
            tmp.close()
            self.api.oauth_login(Mobileclient.FROM_MAC_ADDRESS, tmp.name)
            os.remove(tmp.name)

    def createPlaylist(self, name, songs):
        playlistId = self.api.create_playlist(name=name, description=None, public=False)
        self.addSongs(playlistId, songs)

    def addSongs(self, playlistId, songs):
        songIds = []
        songlist = list(songs)
        notFound = list()
        for i, song in enumerate(songlist):
            result = self.api.search(query=song, max_results=2)
            if len(result['song_hits']) == 0:
                notFound.append(song)
            else:
                songIds.append(self.get_best_fit_song_id(result['song_hits'], song))
            if i % 20 == 0:
                print(str(i) + ' searched')

        self.api.add_songs_to_playlist(playlistId, songIds)

        with open(path + 'noresults.txt', 'w') as f:
            f.write("\n".join(notFound))
            f.close()

    def removeSongs(self, playlistId):
        pl = self.api.get_all_user_playlist_contents()
        tracks = next(x for x in pl if x['id'] == playlistId)['tracks']
        self.api.remove_entries_from_playlist([x['id'] for x in tracks])

    def getPlaylistId(self, name):
        pl = self.api.get_all_playlists()
        return next(x for x in pl if x['name'].find(name) != -1)['id']

    def get_best_fit_song_id(self, results, song):
        match_score = {}
        for res in results:
            compare = res['track']['artist'] + ' ' + res['track']['title']
            match_score[res['track']['storeId']] = difflib.SequenceMatcher(a=song.lower(), b=compare.lower()).ratio()

        return max(match_score, key=match_score.get)

# def remove_playlists(pattern, debug = False):
#     #gmusic = GoogleMusic()
#     #pl = Mobileclient.get_all_playlists(gmusic.api)
#     p = re.compile(pattern)
#     if debug:
#         [print(song['name']) for song in pl if p.match(song['name'])]
#     else:
#         [gmusic.deletePlaylist(song['id']) for song in pl if p.match(song['name'])]

def get_args():
    parser = argparse.ArgumentParser(description='Transfer spotify playlist to Google Play Music.')
    parser.add_argument("playlist", type=str)
    parser.add_argument("-u", "--update", type=str, help="Delete all entries in the provided Google Play Music playlist and update the playlist with entries from the Spotify playlist.")
    parser.add_argument("-n", "--name", type=str, help="Provide a name for the Google Play Music playlist. Default: Spotify playlist name")
    parser.add_argument("-d", "--date", action='store_true', help="Append the current date to the playlist name")
    parser.add_argument("-f", "--file", action='store_true', help="Indicates that the playlist parameter is a filename. Reads playlist entry names from file instead")
    return parser.parse_args()

def main(argv):
    args = get_args()

    gmusic = GoogleMusic()

    date = ""
    if args.date:
        date = " " + datetime.today().strftime('%m/%d/%Y')

    if args.file:
        with open(args.playlist, 'r') as f:
            songs = f.readlines()
        if args.name:
            name = args.name + date
        else:
            name = os.path.basename(args.playlist).split('.')[0] + date
        gmusic.createPlaylist(name, songs)
        return

    playlist = Spotify().getSpotifyPlaylist(args.playlist)

    if args.update:
        playlistId = gmusic.getPlaylistId(args.update)
        gmusic.removeSongs(playlistId)
        gmusic.addSongs(playlistId, playlist['tracks'])
    else:
        if args.name:
            name = args.name + date
        else:
            name = playlist['name'] + date

        gmusic.createPlaylist(name, playlist['tracks'])

if __name__ == "__main__":
    main(sys.argv)