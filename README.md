# Transfer a Spotify Playlist to YouTube Music

A simple command line script to clone a Spotify playlist to YouTube Music.

- Transfer a single Spotify playlist
- Update a transferred playlist on YouTube Music
- Transfer all playlists for a Spotify user
- Remove playlists from YouTube Music


## Install

- Python 3 and pip - https://www.python.org
- Install:

```zsh
$ pip install spotify_to_ytmusic
```

## Setup

1. Generate a new app at https://developer.spotify.com/dashboard
2. Run

```zsh
$ spotify_to_ytmusic setup
```

For backwards compatibility you can also create your own file and pass it using `--file settings.ini`.

## Usage

After you've completed setup, you can simply run the script from the command line using:
```zsh
$ spotify_to_ytmusic create <spotifylink>
```

where `<spotifylink>` is a link like https://open.spotify.com/playlist/0S0cuX8pnvmF7gA47Eu63M

The script will log its progress and output songs that were not found in YouTube Music to **noresults.txt**.

## Transfer all playlists of a Spotify user

For migration purposes, it is possible to transfer all public playlists of a user by using the Spotify user's ID (unique username).

```zsh
$ spotify_to_ytmusic all <spotifyuserid>
```

## Command line options

There are some additional command line options for setting the playlist name and determining whether it's public or not. To view them, run

```zsh
$ spotify_to_ytmusic -h
```

To view subcommand help, run i.e.

```zsh
$ spotify_to_ytmusic setup -h
```

Available subcommands:

```
positional arguments:
  {setup,create,update,remove,all}
                        Provide a subcommand
    setup               Set up credentials
    create              Create a new playlist on YouTube Music.
    update              Delete all entries in the provided Google Play Music playlist and update the playlist with entries from the Spotify playlist.
    remove              Remove playlists with specified regex pattern.
    all                 Transfer all public playlists of the specified user (Spotify User ID).

options:
  -h, --help            show this help message and exit
```
