import difflib
import re
import unicodedata
from ytmusicapi import YTMusic

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

def normalize_text(text):
    """Normalize text by removing unwanted characters and converting to lowercase."""
    # Replace unwanted characters and patterns
    text = re.sub(r"[(),\[\]&]+|feat\.", "", text)
    
    text = re.sub(r"(?<=\s)-(?=\s)", "", text)  # Remove hyphen surrounded by spaces i.e. Brain Deady - Get on my Knees
    text = re.sub(r"(?<=\w)-(?=\w)", " ", text)  # Replace hyphen between letters or numbers with space i.e. Eazy-E
    text = re.sub(r"[\"']", " ", text)  # Replace quotes with a space i.e. Nuthin' But "G" Thang

    # Remove accents and convert to lowercase
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower()

def tokenize(text):
    """Split text into a set of normalized tokens."""
    return set(normalize_text(text).split())

def get_best_fit_song_id_v2(ytm_results: list, spoti: dict, confidence: float = 0.7, tolerance: float = 0.02, api: YTMusic = None, search_albums: bool = False, enable_fallback: bool = False) -> str:
    match_score = {}
    ratios = {}
    music_type = {}
    weights = {"title": 4, "artist": 4, "album": 2, "duration": 5, "boost": 0}

    if confidence is None:
        confidence = 0.7

    if search_albums:
        new_results = []

        for ytm in ytm_results:
            if api and "resultType" in ytm and ytm["resultType"] == "album":
                songs = api.get_album(ytm["browseId"])
                new_results.append(songs)

        # Extend the original list after the loop
        new_results_parsed = []
        for results in new_results:
            for tracks in results["tracks"]:
                tracks["category"] = "Songs"
                tracks["resultType"] = "song"
                tracks["album"] = {
                    "name": tracks["album"]
                }
                new_results_parsed.append(tracks)

        ytm_results.extend(new_results_parsed)

    for ytm in ytm_results:
        if "resultType" not in ytm or ytm["resultType"] not in ["song", "video"] or not ytm.get("title"):
            continue

        # No need to include episodes or other kinds of results
        if "category" not in ytm or ytm["category"] not in ["Top result", "Songs", "Videos"]:
            continue
        # print(ytm['videoId'], ytm["category"])

        # Handle duration matching by @sigma67
        try:
            duration_items = ytm["duration"].split(":")
            duration = int(duration_items[0]) * 60 + int(duration_items[1])
            duration_match_score = 1 - abs(duration - spoti["duration"]) * 2 / spoti["duration"]
        except (ValueError, AttributeError, IndexError):
            duration_match_score = None

        # Preprocess titles and artist lists
        ytm_title = normalize_text(ytm["title"])
        spotify_title = normalize_text(spoti["name"])
        spotify_artists = [normalize_text(artist) for artist in spoti.get("artists_list", [])]

        add_artist_to_artist_list = []

        # Remove artist names from titles if present
        for artist in spotify_artists:
            if artist in ytm_title:
                add_artist_to_artist_list.append(artist)
                ytm_title = ytm_title.replace(artist, "").strip()
            if artist in spotify_title:
                spotify_title = spotify_title.replace(artist, "").strip()

        # Add missing artists to YTM's artist list
        ytm_artists = [normalize_text(a["name"]) for a in ytm.get("artists", [])]

        # print("TITLE: ", ytm_title, spotify_title, "\n")

        for artist in add_artist_to_artist_list:
            if artist not in ytm_artists:
                ytm_artists.append(artist)

        # Tokenize titles
        ytm_tokens = tokenize(ytm_title)
        spotify_tokens = tokenize(spotify_title)

        # Calculate title match score
        common_tokens = ytm_tokens & spotify_tokens
        extra_tokens = ytm_tokens - spotify_tokens
        title_match_score = len(common_tokens) / len(spotify_tokens) - len(extra_tokens) * 0.3
        title_match_score = max(0, title_match_score)  # Ensure score is non-negative

        if title_match_score == 0 or not duration_match_score:
            continue

        # Calculate artist similarity
        artist_similarity = difflib.SequenceMatcher(
            a=" ".join(ytm_artists), b=" ".join(spotify_artists)
        ).ratio()

        # print(" ".join(ytm_artists), " ".join(spotify_artists))

        # Add album similarity for songs only to favor songs over videos
        album_similarity = 0
        # print(ytm.get("album"))
        if ytm["resultType"] == "song" and ytm.get("album"):
            album_name = ytm["album"].get("name", "")
            album_similarity_1 = 0
            album_similarity_2 = 0
            album_similarity_3 = 0
            # print("COMP: ",normalize_text(album_name), "-" ,normalize_text(spoti.get("album", "")), "-", normalize_text(ytm_title), "\n")
            if album_name:
                # If album name is same in both ytm and spotify
                album_similarity_1 = difflib.SequenceMatcher(
                    a=normalize_text(album_name),
                    b=normalize_text(spoti.get("album", "")),
                ).ratio()

                # Sometimes youtube has album name same as song title
                album_similarity_2 = difflib.SequenceMatcher(
                    a=normalize_text(album_name),
                    b=normalize_text(ytm_title),
                ).ratio()

                # Sometimes album name is sometimes same as ytm title
                album_similarity_3 = difflib.SequenceMatcher(
                    a=normalize_text(ytm_title),
                    b=normalize_text(spoti.get("album", "")),
                ).ratio()

                album_similarity = max(album_similarity_1, album_similarity_2, album_similarity_3)
        
        if title_match_score > 0.8 and artist_similarity > 0.7 and duration_match_score < 0:
            # Adjust duration score for shorter versions to match longer ones (to boost good match but bad duration)
            duration_match_score = 0.9
        
        if artist_similarity < 0.3 and album_similarity > 0.7:
            # These are false positives from album similarity
            continue

        # If result is a good match, boost it's score to drown low quality results
        score_boost = 0
        if title_match_score > 0.5 and artist_similarity > 0.5 and album_similarity > 0.5 and duration_match_score > 0.9:
            score_boost = 0.4
        
        # Ensure song is not a clean version if not requested, so explicit version will get explicit version only
        if spoti["is_explicit"] == ytm.get('isExplicit', None):
            score_boost += 1
        else:
            score_boost -= 1
        
        # Top result bais
        if ytm["category"] == "Top result" and ytm["resultType"] == "song" and title_match_score > 0.90 and artist_similarity > 0.90 and duration_match_score > 0.95:
            score_boost += round((weights["title"] + weights["artist"] + weights["duration"])/3)
            # print(f"Applying top result bais adjustment to {ytm['videoId']}...\n")

        # Combine scores with weights
        scores = [
            title_match_score * weights["title"],
            artist_similarity * weights["artist"],
        ]
        if duration_match_score:
            scores.append(duration_match_score * weights["duration"])
        if album_similarity:
            scores.append(album_similarity * weights["album"])
        scores.append(score_boost + weights["boost"])

        # This conditions removes false positives i.e. edge case - Mike Candy's - Vibe instead of Baby - Mike Candy's
        sum_of_weights = sum(scores) / sum(list(weights.values())[: len(scores)])
        
        # print(f"Title Match: {title_match_score}, Type: {ytm['category']}, Explict: { 'Yes' if spoti['is_explicit'] == True else 'No'}, Artist Similarity: {artist_similarity}, Duration Match: {duration_match_score}, Album Similarity: {album_similarity}")

        # Convert weights.values() to a list for slicing
        match_score[ytm["videoId"]] = sum_of_weights
        ratios[ytm["videoId"]] = duration_match_score*title_match_score + sum_of_weights

        music_type[ytm["videoId"]] = ytm["videoType"]
        
        # print(f"Final Score for {ytm['videoId']}: {match_score[ytm['videoId']]}\n\n")


    if not match_score:
        return None

    # Sort match scores in descending order and keep top 3
    sorted_matches = sorted(match_score.items(), key=lambda x: x[1], reverse=True)
    top_3_matches = sorted_matches[:3]

    # Build best_ratios from top 3 matches
    best_ratios = {videoId: ratios.get(videoId) for videoId, _ in top_3_matches}
    max_score = max(best_ratios.values())

    # Find all video IDs with the maximum score
    max_video_ids = [videoId for videoId, score in best_ratios.items() if score == max_score]

    # Function to select a video by preferred type (prioritizing ATV over OMV)
    def select_audio_over_video(video_ids):
        for video_id in video_ids:
            if music_type.get(video_id) == "MUSIC_VIDEO_TYPE_ATV":
                return video_id
        for video_id in video_ids:
            if music_type.get(video_id) == "MUSIC_VIDEO_TYPE_OMV":
                return video_id
        return None  # No ATV or OMV match

    # Handle tie or no-tie cases
    if len(max_video_ids) > 1:
        # print("TIE! Prioritizing ATV over OMV...")
        best_video_id = select_audio_over_video(max_video_ids)
    else:
        # print("No tie. Prioritizing ATV over OMV...")
        best_video_id = select_audio_over_video(best_ratios.keys())

    # If a preferred video was selected and meets confidence requirements, return it
    if best_video_id:
        best_score = match_score.get(best_video_id)
        if best_score >= (confidence - tolerance):
            return best_video_id

    # Fall back to the highest scoring match
    best_video_id, best_score = max(best_ratios.items(), key=lambda x: x[1])
    if best_score >= (confidence - tolerance):
        return best_video_id

    # Fallback to default algorithm if enabled
    if enable_fallback:
        # print("Fallback to default algorithm.")
        return get_best_fit_song_id(ytm_results, spoti)

    # No valid match found
    return None
