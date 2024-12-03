import difflib


def get_best_fit_song_id(ytm_results, spoti) -> str:
    """
    Find the best match for track spoti in a list of ytmusicapi results

    :param ytm_results: List of ytmusicapi search results
    :param spoti: Spotify track
    :return: videoId of best matching result
    """
    match_score = {}
    title_score = {}
    for ytm in ytm_results:
        if (
            "resultType" not in ytm
            or ytm["resultType"] not in ["song", "video"]
            or not ytm["title"]
        ):
            continue

        duration_match_score = None
        if "duration" in ytm and ytm["duration"] and spoti["duration"]:
            duration_items = ytm["duration"].split(":")
            duration = int(duration_items[0]) * 60 + int(duration_items[1])
            duration_match_score = 1 - abs(duration - spoti["duration"]) * 2 / spoti["duration"]

        title = ytm["title"]
        # for videos,
        if ytm["resultType"] == "video":
            title_split = title.split("-")
            if len(title_split) == 2:
                title = title_split[1]

        artists = " ".join([a["name"] for a in ytm["artists"]])

        title_score[ytm["videoId"]] = difflib.SequenceMatcher(
            a=title.lower(), b=spoti["name"].lower()
        ).ratio()
        scores = [
            title_score[ytm["videoId"]],
            difflib.SequenceMatcher(a=artists.lower(), b=spoti["artist"].lower()).ratio(),
        ]
        if duration_match_score:
            scores.append(duration_match_score * 5)

        # add album for songs only
        if ytm["resultType"] == "song" and ytm.get("album", None) is not None:
            scores.append(
                difflib.SequenceMatcher(
                    a=ytm["album"]["name"].lower(), b=spoti["album"].lower()
                ).ratio()
            )

        match_score[ytm["videoId"]] = (
            sum(scores) / len(scores) * max(1, int(ytm["resultType"] == "song") * 2)
        )

    if len(match_score) == 0:
        return None

    max_score_video_id = max(match_score, key=match_score.get)

    return max_score_video_id

def get_best_fit_song_id_v2(ytm_results, spoti) -> str:
    """
    Find the best match for a Spotify track in a list of YTMusic search results.

    The function implements strict matching logic:
    - Matches only if the calculated accuracy score is at least 70%.
    - Incorporates title, artist, album, and duration matching.

    :param ytm_results: List of YTMusic search results (e.g., from self.api.search()).
    :param spoti: Spotify track details.
    :return: videoId of the best matching result or None if no match exceeds the threshold.
    """
    match_score = {}

    for ytm in ytm_results:
        # Skip results that don't have essential fields or aren't songs/videos
        if (
            "resultType" not in ytm
            or ytm["resultType"] not in ["song", "video"]
            or not ytm.get("title")
        ):
            continue

        # Calculate duration match score (normalized)
        duration_match_score = None
        if "duration" in ytm and ytm["duration"] and spoti.get("duration"):
            duration_items = ytm["duration"].split(":")
            duration = int(duration_items[0]) * 60 + int(duration_items[1])
            duration_match_score = 1 - abs(duration - spoti["duration"]) * 2 / spoti["duration"]

        # Process title and handle videos with "Artist - Title" structure
        title = ytm["title"]
        if ytm["resultType"] == "video" and "-" in title:
            title_split = title.split("-")
            if len(title_split) == 2:
                title = title_split[1].strip()

        # Extract artist names
        artists = " ".join([a["name"] for a in ytm["artists"]])

        # Calculate similarity scores
        title_similarity = difflib.SequenceMatcher(
            a=title.lower(), b=spoti["name"].lower()
        ).ratio()
        artist_similarity = difflib.SequenceMatcher(
            a=artists.lower(), b=spoti["artist"].lower()
        ).ratio()

        # Add album similarity for songs only
        album_similarity = 0
        if ytm["resultType"] == "song" and ytm.get("album", None):
            album_similarity = difflib.SequenceMatcher(
                a=ytm["album"]["name"].lower(), b=spoti["album"].lower()
            ).ratio()

        # Combine scores with weights
        scores = [title_similarity * 4, artist_similarity * 4]
        if duration_match_score:
            scores.append(duration_match_score * 5)
        if album_similarity:
            scores.append(album_similarity * 2)

        # Calculate the weighted match score
        match_score[ytm["videoId"]] = sum(scores) / sum([4, 4, 5, 2][: len(scores)])

    # Filter matches by threshold
    if not match_score:
        return None
    best_video_id, best_score = max(match_score.items(), key=lambda x: x[1])

    # Only return if the best match exceeds 70%
    if best_score >= 0.7:
        return best_video_id
    return None