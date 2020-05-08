from gmusicapi import session, Mobileclient
from SpotifyExport import Spotify
import os
import re
import json
import difflib
import settings
import argparse
import reddit
from datetime import datetime

path = os.path.dirname(os.path.realpath(__file__)) + os.sep


class GoogleMusic:
    def __init__(self):
        self.api = Mobileclient(debug_logging=False)
        refresh_token = json.loads(settings['google']['mobileclient'])['refresh_token']
        credentials = session.credentials_from_refresh_token(refresh_token, session.Mobileclient.oauth)
        self.api.oauth_login(Mobileclient.FROM_MAC_ADDRESS, credentials)

    def createPlaylist(self, name, description, songs, public):
        playlistId = self.api.create_playlist(name=name, description=description, public=public)
        self.addSongs(playlistId, songs)
        print("Success: created playlist \"" + name + "\"")

    def addSongs(self, playlistId, songs):
        songIds = []
        songlist = list(songs)
        notFound = list()
        for i, song in enumerate(songlist):
            query = song['artist'] + ' ' + song['name']
            query = query.replace(" &", "")
            result = self.api.search(query=query, max_results=2)
            if len(result['song_hits']) == 0:
                notFound.append(query)
            else:
                songIds.append(self.get_best_fit_song_id(result['song_hits'], song))
            if i % 20 == 0:
                print(str(i) + ' searched')

        self.api.add_songs_to_playlist(playlistId, songIds)

        with open(path + 'noresults.txt', 'w', encoding="utf-8") as f:
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
            artist_score = difflib.SequenceMatcher(a=res['track']['artist'].lower(), b=song['artist'].lower()).ratio()
            title_score = difflib.SequenceMatcher(a=res['track']['title'].lower(), b=song['name'].lower()).ratio()
            album_score = difflib.SequenceMatcher(a=res['track']['album'].lower(), b=song['album'].lower()).ratio()
            match_score[res['track']['storeId']] = (artist_score + title_score + album_score) / 3

        return max(match_score, key=match_score.get)

    def remove_playlists(self, pattern):
        pl = self.api.get_all_playlists()
        p = re.compile("{0}".format(pattern))
        matches = [song for song in pl if p.match(song['name'])]
        print("The following playlists will be removed:")
        print("\n".join([song['name'] for song in matches]))
        print("Please confirm (y/n):")

        choice = input().lower()
        if choice[:1] == 'y':
            [self.api.delete_playlist(song['id']) for song in matches]
            print(str(len(matches)) + " playlists deleted.")
        else:
            print("Aborted. No playlists were deleted.")


def get_args():
    parser = argparse.ArgumentParser(description='Transfer spotify playlist to Google Play Music.')
    parser.add_argument("playlist", type=str, help="Provide a playlist Spotify link. Alternatively, provide a text file (one song per line)")
    parser.add_argument("-u", "--update", type=str, help="Delete all entries in the provided Google Play Music playlist and update the playlist with entries from the Spotify playlist.")
    parser.add_argument("-n", "--name", type=str, help="Provide a name for the Google Play Music playlist. Default: Spotify playlist name")
    parser.add_argument("-i", "--info", type=str, help="Provide description information for the Google Play Music Playlist. Default: Spotify playlist description")
    parser.add_argument("-d", "--date", action='store_true', help="Append the current date to the playlist name")
    parser.add_argument("-p", "--public", action='store_true', help="Make the playlist public. Default: private")
    parser.add_argument("-r", "--remove", action='store_true', help="Remove playlists with specified regex pattern.")
    parser.add_argument("-re", "--reddit", action='store_true', help="Post to latest r/EDM reddit thread.")
    parser.add_argument("-a", "--all", action='store_true', help="Transfer all public playlists of the specified user (Spotify User ID).")
    return parser.parse_args()

def main():
    args = get_args()
    gmusic = GoogleMusic()

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
                gmusic.createPlaylist(p['name'], p['description'], playlist['tracks'], args.public)
            except Exception as ex:
                print("Could not transfer playlist")
        return

    if args.remove:
        gmusic.remove_playlists(args.playlist)
        return

    date = ""
    if args.date:
        date = " " + datetime.today().strftime('%m/%d/%Y')

    if os.path.isfile(args.playlist):
        with open(args.playlist, 'r') as f:
            songs = f.readlines()
        if args.name:
            name = args.name + date
        else:
            name = os.path.basename(args.playlist).split('.')[0] + date
        gmusic.createPlaylist(name, args.info, songs, args.public)
        return

    try:
        playlist = Spotify().getSpotifyPlaylist(args.playlist)
    except Exception as ex:
        print("Could not get Spotify playlist. Please check the playlist link.\n Error: " + repr(ex))
        return

    if args.update:
        playlistId = gmusic.getPlaylistId(args.update)
        gmusic.removeSongs(playlistId)
        gmusic.addSongs(playlistId, playlist['tracks'])
    else:
        name = args.name + date if args.name else playlist['name'] + date
        info = playlist['description'] if (args.info is None) else args.info
        gmusic.createPlaylist(name, info, playlist['tracks'], args.public)

    if args.reddit:
        pl = gmusic.api.get_all_playlists()
        shareToken = next(x for x in pl if x['name'].find(name) != -1)['shareToken']
        comment = "[Google Play Music](https://play.google.com/music/playlist/" + shareToken + ")"
        with open(path + "comment.txt", 'a') as f:
            f.write(comment)

if __name__ == "__main__":
    main()