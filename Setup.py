import sys
import settings
import socket

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

if __name__ == "__main__":

    if sys.argv[1] == "mobileclient":
        from gmusicapi import Mobileclient
        api = Mobileclient(debug_logging=True)
        settings['google']['mobileclient'] = api.perform_oauth(open_browser=True).to_json()

    elif sys.argv[1] == "musicmanager":
        from gmusicapi import Musicmanager
        api = Musicmanager(debug_logging=True)
        settings['google']['musicmanager'] = api.perform_oauth(open_browser=True).to_json()

    elif sys.argv[1] == "youtube":
        from ytmusicapi import YTMusic
        api = YTMusic()
        settings['youtube']['headers'] = api.setup()

    elif sys.argv[1] == "reddit":
        import praw
        agent = 'Gmusic playlist app by /u/Sigmatics'

        reddit = praw.Reddit(client_id=settings['reddit']['client_id'],
                             client_secret=settings['reddit']['client_secret'],
                             redirect_uri='http://localhost:8080',
                             user_agent=agent)

        print(reddit.auth.url(['identity', 'read', 'submit'], '322', 'permanent'))

        client = receive_connection()
        data = client.recv(1024).decode("utf-8")
        param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
        params = {
            key: value
            for (key, value) in [token.split("=") for token in param_tokens]
        }
        settings['reddit']['refresh_token'] = reddit.auth.authorize(params["code"])

    settings.save()
