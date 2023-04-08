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
        if "resultType" not in ytm or ytm["resultType"] not in ["song", "video"]:
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
        if ytm["resultType"] == "song" and ytm["album"] is not None:
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
