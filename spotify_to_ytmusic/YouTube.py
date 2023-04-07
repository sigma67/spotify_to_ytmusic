from ytmusicapi import YTMusic
import os
import re
import difflib
from collections import OrderedDict
import settings

path = os.path.dirname(os.path.realpath(__file__)) + os.sep


class YTMusicTransfer:
    def __init__(self):
        self.api = YTMusic(settings['youtube']['headers'], settings['youtube']['user_id'])

    def create_playlist(self, name, info, privacy="PRIVATE", tracks=None):
        return self.api.create_playlist(name, info, privacy, video_ids=tracks)

    def get_best_fit_song_id(self, results, song):
        match_score = {}
        title_score = {}
        for res in results:
            if 'resultType' not in res or res['resultType'] not in ['song', 'video']:
                continue

            durationMatch = None
            if 'duration' in res and res['duration'] and song['duration']:
                durationItems = res['duration'].split(':')
                duration = int(durationItems[0]) * 60 + int(durationItems[1])
                durationMatch = 1 - abs(duration - song['duration']) * 2 / song['duration']

            title = res['title']
            # for videos,
            if res['resultType'] == 'video':
                titleSplit = title.split('-')
                if len(titleSplit) == 2:
                    title = titleSplit[1]

            artists = ' '.join([a['name'] for a in res['artists']])

            title_score[res['videoId']] = difflib.SequenceMatcher(a=title.lower(), b=song['name'].lower()).ratio()
            scores = [title_score[res['videoId']],
                      difflib.SequenceMatcher(a=artists.lower(), b=song['artist'].lower()).ratio()]
            if durationMatch:
                scores.append(durationMatch * 5)

            #add album for songs only
            if res['resultType'] == 'song' and res['album'] is not None:
                scores.append(difflib.SequenceMatcher(a=res['album']['name'].lower(), b=song['album'].lower()).ratio())

            match_score[res['videoId']] = sum(scores) / len(scores) * max(1, int(res['resultType'] == 'song') * 2)

        if len(match_score) == 0:
            return None

        max_score = max(match_score, key=match_score.get)
        return max_score

    def search_songs(self, tracks):
        videoIds = []
        songs = list(tracks)
        notFound = list()
        for i, song in enumerate(songs):
            name = re.sub(r' \(feat.*\..+\)', '', song['name'])
            query = song['artist'] + ' ' + name
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

            print("Searching YouTube...")
            if i > 0 and i % 10 == 0:
                print(f"YouTube tracks: {i}/{len(songs)}")

        with open(path + 'noresults_youtube.txt', 'w', encoding="utf-8") as f:
            f.write("\n".join(notFound))
            f.write("\n")
            f.close()

        return videoIds

    def add_playlist_items(self, playlistId, videoIds):
        videoIds = OrderedDict.fromkeys(videoIds)
        self.api.add_playlist_items(playlistId, videoIds)

    def get_playlist_id(self, name):
        pl = self.api.get_library_playlists(10000)
        try:
            playlist = next(x for x in pl if x['title'].find(name) != -1)['playlistId']
            return playlist
        except:
            raise Exception("Playlist title not found in playlists")

    def remove_songs(self, playlistId):
        items = self.api.get_playlist(playlistId, 10000)
        if 'tracks' in items:
            self.api.remove_playlist_items(playlistId, items['tracks'])

    def remove_playlists(self, pattern):
        playlists = self.api.get_library_playlists(10000)
        p = re.compile("{0}".format(pattern))
        matches = [pl for pl in playlists if p.match(pl['title'])]
        print("The following playlists will be removed:")
        print("\n".join([pl['title'] for pl in matches]))
        print("Please confirm (y/n):")

        choice = input().lower()
        if choice[:1] == 'y':
            [self.api.delete_playlist(pl['playlistId']) for pl in matches]
            print(str(len(matches)) + " playlists deleted.")
        else:
            print("Aborted. No playlists were deleted.")

