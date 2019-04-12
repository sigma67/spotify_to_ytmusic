import praw
import settings
import socket
import time

agent = 'Gmusic playlist app by /u/Sigmatics'
def receive_connection():
    """Wait for and then return a connected socket..

    Opens a TCP connection on port 8080, and waits for a single client.

    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client

def setup():
    reddit = praw.Reddit(client_id=settings['reddit']['client_id'],
                         client_secret=settings['reddit']['client_secret'],
                         redirect_uri='http://localhost:8080',
                         user_agent=agent)

    print(reddit.auth.url(['identity', 'read', 'submit'], '...', 'permanent'))

    client = receive_connection()
    data = client.recv(1024).decode("utf-8")
    param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
    params = {
        key: value
        for (key, value) in [token.split("=") for token in param_tokens]
    }

    settings['reddit']['refresh_token'] = reddit.auth.authorize(params["code"])


class Reddit:
    def __init__(self):
        if settings['reddit']['refresh_token'] == "":
            print("Please run setup first!")
            return

        self.reddit = praw.Reddit(client_id=settings['reddit']['client_id'],
                             client_secret=settings['reddit']['client_secret'],
                             refresh_token=settings['reddit']['refresh_token'],
                             user_agent=agent)

    def comment_EDM(self, content):
        sub = self.reddit.subreddit('EDM')
        results = sub.search("New EDM This Week", time_filter="week")
        for x in results:
            if time.time() - x.created_utc < 86400:
                print("Commenting post: " + x.title)
                x.reply(content)
