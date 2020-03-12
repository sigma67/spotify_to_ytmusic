from ytmusicapi import YTMusic
from datetime import datetime
import os
import argparse
import difflib
from SpotifyExport import Spotify

path = os.path.dirname(os.path.realpath(__file__)) + os.sep


class YTMusicTransfer:
    def __init__(self):
        self.api = YTMusic(path + 'headers_auth.json')

    def create_playlist(self, name, info, privacy="PRIVATE"):
        return self.api.create_playlist(name, info, privacy)

    def get_best_fit_song_id(self, results, song):
        match_score = {}
        title_score = {}
        for res in results:
            if res['resultType'] not in ['song', 'video']:
                continue

            #remove artists from target song title for videos
            title = res['title']
            if res['resultType'] == 'video':
                for a in song['artist'].split(' '):
                    title = title.replace(a, '')

            title_score[res['videoId']] = difflib.SequenceMatcher(a=title.lower(), b=song['name'].lower()).ratio()
            scores = [title_score[res['videoId']],
                      difflib.SequenceMatcher(a=res['artist'].lower(), b=song['artist'].lower()).ratio()]

            #add album for songs only
            if res['resultType'] == 'song' and 'album' in res:
                scores.append(difflib.SequenceMatcher(a=res['album'].lower(), b=song['album'].lower()).ratio())

            match_score[res['videoId']] = sum(scores) / len(scores)

        #don't return songs with titles <45% match
        max_score = max(match_score, key=match_score.get)
        return max_score if title_score[max_score] > 0.45 else None

    def search_songs(self, tracks):
        videoIds = []
        songs = list(tracks)
        notFound = list()
        for i, song in enumerate(songs):
            query = song['artist'] + ' ' + song['name']
            query = query.replace(" &", "")
            result = self.api.search(query)
            if len(result) == 0:
                notFound.append(query)
            else:
                targetSong = self.get_best_fit_song_id(result, song)
                if targetSong is None:
                    notFound.append(query)
                else:
                    videoIds.append(targetSong)

            if i > 0 and i % 10 == 0:
                print(str(i) + ' searched')

        return videoIds, notFound

    def add_songs(self, playlist, tracks):
        videoIds, notFound = self.search_songs(tracks)

        self.api.add_playlist_items(playlist, videoIds)

        with open(path + 'noresults_youtube.txt', 'w', encoding="utf-8") as f:
            f.write("\n".join(notFound))
            f.close()

    def get_playlist_id(self, name):
        result = {}
        try:
            result = self.api.search(name, 'playlists')[0]
        except Exception as e:
            print(e)

        return result['browseId'][2:]

    def remove_songs(self, playlistId):
        items = self.api.get_playlist_items(playlistId)
        if len(items) > 0:
            self.api.remove_playlist_items(playlistId, items)


def get_args():
    parser = argparse.ArgumentParser(description='Transfer spotify playlist to YouTube Music.')
    parser.add_argument("playlist", type=str, help="Provide a playlist Spotify link. Alternatively, provide a text file (one song per line)")
    parser.add_argument("-u", "--update", type=str, help="Delete all entries in the provided Google Play Music playlist and update the playlist with entries from the Spotify playlist.")
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

    if args.update:
        playlistId = ytmusic.get_playlist_id(args.update)
        ytmusic.remove_songs(playlistId)
        ytmusic.add_songs(playlistId, playlist['tracks'])

    else:
        playlistId = ytmusic.create_playlist(name, info, 'PUBLIC' if args.public else 'PRIVATE')
        ytmusic.add_songs(playlistId, playlist['tracks'])

        comment = "[YouTube Music](https://music.youtube.com/playlist?list=" + playlistId + ")"
        with open(path + "comment.txt", 'a') as f:
            f.write(comment)

        print("Success: created playlist \"" + name + "\"")


if __name__ == "__main__":
    main()