from spotify_to_ytmusic.utils.match import get_best_fit_song_id

SPOTIFY_TRACK = {
    "name": "Wonderwall",
    "artist": "Oasis",
    "album": "(What's The Story) Morning Glory?",
    "duration": 259,
}


def make_result(**overrides):
    result = {
        "resultType": "song",
        "videoId": "good",
        "title": "Wonderwall",
        "artists": [{"name": "Oasis", "id": "UCmMUZbaYdNH0bEd1PAlAqsA"}],
        "album": {
            "name": "(What's The Story) Morning Glory?",
            "id": "MPREb_9nqEki4ZDpp",
        },
        "duration": "4:19",
    }
    result.update(overrides)
    return result


class TestGetBestFitSongId:
    def test_picks_best_match(self):
        results = [
            make_result(videoId="other", title="Champagne Supernova"),
            make_result(),
        ]
        assert get_best_fit_song_id(results, SPOTIFY_TRACK) == "good"

    def test_no_results(self):
        assert get_best_fit_song_id([], SPOTIFY_TRACK) is None

    def test_result_without_artists(self):
        result = make_result()
        del result["artists"]
        assert get_best_fit_song_id([result], SPOTIFY_TRACK) == "good"

    def test_result_with_null_artists(self):
        results = [make_result(artists=None)]
        assert get_best_fit_song_id(results, SPOTIFY_TRACK) == "good"

    def test_result_with_nameless_artist(self):
        results = [make_result(artists=[{"id": "x"}])]
        assert get_best_fit_song_id(results, SPOTIFY_TRACK) == "good"

    def test_result_without_album_name(self):
        results = [make_result(album={"id": "x"})]
        assert get_best_fit_song_id(results, SPOTIFY_TRACK) == "good"

    def test_skips_unusable_results(self):
        no_video_id = make_result()
        del no_video_id["videoId"]
        no_title = make_result(videoId="no_title")
        del no_title["title"]
        no_type = make_result(videoId="no_type")
        del no_type["resultType"]
        results = [
            no_video_id,
            no_title,
            no_type,
            make_result(videoId="artist", resultType="artist"),
        ]
        assert get_best_fit_song_id(results, SPOTIFY_TRACK) is None

    def test_skips_unusable_but_keeps_valid(self):
        broken = make_result(videoId="broken")
        del broken["title"]
        assert get_best_fit_song_id([broken, make_result()], SPOTIFY_TRACK) == "good"
