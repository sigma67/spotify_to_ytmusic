import re

from spotify_to_ytmusic.controllers import _init, comment


def top(args):
    spotify, ytmusic = _init()
    from spotify_to_ytmusic.reddit import Reddit
    r = Reddit()
    track_counts = []

    results = r.get_top_new()
    playlist = {'tracks': [], 'description': 'Top submissions'}
    for r in results['spotify']:
        tracks = spotify.get_tracks(r)
        playlist['tracks'].extend(tracks)
        track_counts.append(len(tracks))

    search_results = ytmusic.search_songs(playlist['tracks'])

    videoIds = []
    counter = 0
    track_counter = 0
    for i in range(len(results['youtube'] + results['spotify'])):
        if i in results['youtube_pos']:
            r = results['youtube'][results['youtube_pos'].index(i)]
            match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', r)  # from pytube extract.video_id
            videoIds.append(match.group(1))
        else:
            videoIds.extend(search_results[track_counter:track_counter + track_counts[counter]])
            track_counter += track_counts[counter]
            counter += 1

    if args.update:
        playlist_id = ytmusic.get_playlist_id(args.name)
        if len(videoIds) > 0:
            ytmusic.remove_songs(playlist_id)
        ytmusic.add_playlist_items(playlist_id, videoIds)
    else:
        playlist_id = ytmusic.create_playlist(args.name, args.info, 'PUBLIC' if args.public else 'PRIVATE', videoIds)
        comment(args.comment, playlist_id)
