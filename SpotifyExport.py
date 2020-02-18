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
        playlistId = url_parts[4].split('?')[0]
        if len(playlistId) != 22:
            raise Exception('Bad playlist id: ' + playlistId)

        tracks = []
        results = self.api.playlist(playlistId)
        name = results['name']
        tracks += list(track['track']['artists'][0]['name'] + ' ' + track['track']['name'] for track in results['tracks']["items"] if track['track'] is not None)

        count = 1
        more = len(results['tracks']['items']) == 100
        while more:
            items = self.api.playlist_tracks(playlistId, offset = count * 100, limit=100)
            print('requested from ' + str(count * 100))
            tracks += list(track['track']['artists'][0]['name'] + ' ' + track['track']['name'] for track in items["items"] if track['track'] is not None)
            more = len(items["items"]) == 100
            count = count + 1

        return {'tracks': tracks, 'name': name, 'description': results['description']}

    def getUserPlaylists(self, user):
        pl = self.api.user_playlists(user)['items']
        count = 1
        more = len(pl) == 50
        while more:
            results = self.api.user_playlists(user, offset=count * 50)['items']
            pl.extend(results)
            more = len(results) == 50
            count = count + 1

        return [p for p in pl if p['owner']['display_name'] == user and p['tracks']['total'] > 0]