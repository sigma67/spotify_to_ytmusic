# Transfer a Spotify Playlist to YouTube Music

A simple command line script to clone a Spotify playlist to YouTube Music. 

- Transfer a single Spotify playlist
- Transfer all playlists for a Spotify user


## Requirements

- Python 3 - https://www.python.org
- Python extensions: `pip install -U -r requirements`
- Have made at least one playlist manually on YouTube Music

## Setup

1. Initially you should create a new `settings.ini` containing your Spotify credentials. 

Simply copy `settings.ini.example` to a new file `settings.ini`:

```zsh
$ cp settings.ini.example settings.ini
```

2. Generate a new app at https://developer.spotify.com/my-applications

3. Fill in your `client_id` and `client_secret` from your Spotify app

4. For YouTube Music, open a console in the source code folder and run 

`python Setup.py youtube`

Then, open your browser and copy your request headers according to the instructions at https://ytmusicapi.readthedocs.io/en/latest/setup.html 

All credentials are stored locally in the file `settings.ini`. 

## Transfer a playlist

After you've created the settings file, you can simply run the script from the command line using:

`python YouTube.py <spotifylink>`

where `<spotifylink>` is a link like https://open.spotify.com/user/edmsauce/playlist/3yGp845Tz2duWCORALQHFO
Alternatively you can also **use a file name** in place of a spotify link. The file should contain one song per line.

The script will log its progress and output songs that were not found in YouTube Music to **noresults.txt**.

## Transfer all playlists of a Spotify user

For migration purposes, it is possible to transfer all public playlists of a user by using the Spotify user's ID (unique username).

`python YouTube.py --all <spotifyuserid>`


## Command line options

There are some additional command line options for setting the playlist name and determining whether it's public or not. To view them, run

`> python YouTube.py -h`

Arguments:

```
positional arguments:
  playlist              Provide a playlist Spotify link. Alternatively,
                        provide a text file (one song per line)

optional arguments:
  -h, --help            show this help message and exit
  -u UPDATE, --update UPDATE
                        Delete all entries in the provided YouTube Music
                        playlist and update the playlist with entries from the
                        Spotify playlist.
  -n NAME, --name NAME  Provide a name for the YouTube Music playlist.
                        Default: Spotify playlist name
  -i INFO, --info INFO  Provide description information for the YouTube
                        Music Playlist. Default: Spotify playlist description
  -d, --date            Append the current date to the playlist name
  -p, --public          Make the playlist public. Default: private
  -r, --remove          Remove playlists with specified regex pattern.
  -a, --all             Transfer all public playlists of the specified user
                        (Spotify User ID).
```
