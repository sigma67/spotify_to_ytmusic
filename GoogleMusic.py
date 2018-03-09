from gmusicapi import Mobileclient
from SpotifyExport import Spotify
import sys
import difflib
import settings

class GoogleMusic:
    def __init__(self):
        conf = settings['google']
        self.api = Mobileclient()
        self.api.login(conf['email'], conf['password'], Mobileclient.FROM_MAC_ADDRESS)

    def createPlaylist(self, name, songs):
        playlistId = Mobileclient.create_playlist(self.api, name=name, description=None, public=False)
        self.addSongs(playlistId, songs)

    def addSongs(self, playlistId, songs):
        songIds = []
        songlist = list(songs)
        notFound = list()
        for i, song in enumerate(songlist):
            result = Mobileclient.search(self.api, query=song, max_results=2)
            if len(result['song_hits']) == 0:
                notFound.append(song)
            else:
                songIds.append(self.get_best_fit_song_id(result['song_hits'], song))
            if i % 20 == 0:
                print(str(i) + ' searched')

        Mobileclient.add_songs_to_playlist(self.api, playlistId, songIds)

        with open('noresults.txt', 'w') as f:
            f.write("\n".join(notFound))
            f.close()


    def getPlaylistId(self, name):
        pl = Mobileclient.get_all_playlists(self.api)
        return next(x for x in pl if x['name'].find(name) != -1)['id']

    def get_best_fit_song_id(self, results, song):
        match_score = {}
        for res in results:
            compare = res['track']['artist'] + ' ' + res['track']['title']
            match_score[res['track']['storeId']] = difflib.SequenceMatcher(a=song.lower(), b=compare.lower()).ratio()

        return max(match_score, key=match_score.get)

def main(argv):
    if len(argv) < 2:
        print('not enough arguments')
        pass
    else:
        gmusic = GoogleMusic()
        playlist = Spotify().getSpotifyPlaylist(argv[1])
        if len(argv) == 2:
            gmusic.createPlaylist(playlist[1], playlist[0])
        elif len(argv) == 3:
            gmusic.addSongs(gmusic.getPlaylistId(argv[2]), playlist[0])
    pass


if __name__ == "__main__":
    main(sys.argv)