import os
import sys
import time
from pathlib import Path

import praw

from spotify_to_ytmusic.settings import Settings

agent = "ytmusic playlist app by /u/Sigmatics"


class Reddit:
    def __init__(self):
        settings = Settings()
        if settings["reddit"]["refresh_token"] == "":
            print("Please run setup first!")
            sys.exit(1)

        self.reddit = praw.Reddit(
            client_id=settings["reddit"]["client_id"].strip(),
            client_secret=settings["reddit"]["client_secret"].strip(),
            refresh_token=settings["reddit"]["refresh_token"].strip(),
            user_agent=agent,
        )

    def comment_EDM(self, content, days):
        sub = self.reddit.subreddit("EDM")
        query = 'title:"New EDM This Week"'
        results = sub.search(query, time_filter="week")
        commented = False
        for x in results:
            if time.time() - x.created_utc < days * 86400:
                print("Commenting post: " + x.title)
                x.reply(content)
                commented = True
                break

        return commented

    def get_top_new(self, time="week"):
        print("Fetching reddit content...")
        sub = self.reddit.subreddit("EDM")
        query = 'flair:"new music"'
        results = sub.search(query, time_filter=time, sort="top")
        urls = [x.url for x in results]
        spotify = []
        youtube = []
        youtube_pos = []
        count = 0
        for url in urls:
            print(url)
            if "open.spotify.com" in url:
                spotify.append(url)
                count += 1
            elif "youtu.be" in url or "youtube.com/watch?v=" in url:
                youtube.append(url)
                youtube_pos.append(count)
                count += 1
        return {
            "spotify": spotify,
            "youtube": youtube,
            "youtube_pos": youtube_pos,
        }


def comment_edm(args):
    filename = Path.cwd().joinpath("comment.txt")
    if not os.path.isfile(filename):
        exit()
    f = open(filename, "r")
    comment = f.read()
    r = Reddit()
    success = r.comment_EDM(comment, args.days)
    if success:
        os.remove(filename)
