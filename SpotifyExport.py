from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import settings

class Spotify:
    def __init__(self):
        conf = settings['spotify']
        client_credentials_manager = SpotifyClientCredentials(client_id=conf['client_id'], client_secret=conf['client_secret'])
        self.api = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def getSpotifyPlaylist(self, url):
        url_parts = url.split('/')
        user = url_parts[4]
        playlistId = url_parts[6].split('?')[0]
        if len(playlistId) != 22:
            return ('Bad playlist id: ' + playlistId)

        tracks = []
        results = self.api.user_playlist(user, playlistId)
        name = results['name']
        tracks += list(track['track']['artists'][0]['name'] + ' ' + track['track']['name'] for track in results['tracks']["items"] if track['track'] is not None)

        count = 1
        more = len(results['tracks']['items']) == 100
        while more:
            results = self.api.user_playlist_tracks(user, playlistId, offset = count * 100, limit=100)
            print('requested from ' + str(count * 100))
            tracks += list(track['track']['artists'][0]['name'] + ' ' + track['track']['name'] for track in results["items"] if track['track'] is not None)
            more = len(results["items"]) == 100
            count = count + 1

        return [tracks, name]