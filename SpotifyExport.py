from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import settings
import html


class Spotify:
    def __init__(self):
        conf = settings['spotify']
        client_credentials_manager = SpotifyClientCredentials(client_id=conf['client_id'], client_secret=conf['client_secret'])
        self.api = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def getSpotifyPlaylist(self, url):
        playlistId = get_id_from_url(url)
        if len(playlistId) != 22:
            raise Exception('Bad playlist id: ' + playlistId)

        results = self.api.playlist(playlistId)
        name = results['name']
        total = int(results['tracks']['total'])
        tracks = build_results(results['tracks']['items'])
        count = len(tracks)
        print(f"Spotify tracks: {count}/{total}")

        while count < total:
            more_tracks = self.api.playlist_items(playlistId, offset=count, limit=100)
            tracks += build_results(more_tracks['items'])
            count = count + 100
            print(f"Spotify tracks: {count}/{total}")

        return {'tracks': tracks, 'name': name, 'description': html.unescape(results['description'])}

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

    def get_tracks(self, url):
        tracks = []
        id = get_id_from_url(url)
        if 'album' in url:
            album = self.api.album(id)
            tracks.extend(build_results(album['tracks']['items'], album['name']))
        elif 'track' in url:
            track = self.api.track(id)
            tracks.extend(build_results([track]))
        return tracks


def build_results(tracks, album=None):
    results = []
    for track in tracks:
        if 'track' in track:
            track = track['track']
        if not track:
            continue
        album_name = album if album else track['album']['name']
        results.append({
            'artist': ' '.join([artist['name'] for artist in track['artists']]),
            'name': track['name'],
            'album': album_name,
            'duration': track['duration_ms']/1000
        })

    return results


def get_id_from_url(url):
    url_parts = url.split('/')
    return url_parts[4].split('?')[0]