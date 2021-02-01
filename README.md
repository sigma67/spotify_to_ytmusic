# Transfer a Spotify Playlist to Google Play Music

A simple command line script to clone a Spotify playlist to Google Play Music. 

- Transfer a single Spotify playlist
- Transfer all playlists for a Spotify user

Also includes interfaces to:

- Create a Play Music playlist from a text file
- Upload local MP3s to Play Music

**New:** YouTube Music support. Spotify playlists can now be transferred to YouTube Music thanks to [ytmusicapi](https://github.com/sigma67/ytmusicapi).
Usage is identical to GoogleMusic.py, just use `python YouTube.py` with the same parameters.

## Requirements

- Python 3 - https://www.python.org
- Python extensions: `pip install -U -r requirements`

## Setup

1. Initially you should create a new `settings.ini` containing your Spotify credentials. 

Simply copy `settings.ini.example` to a new file `settings.ini`:

```zsh
$ cp settings.ini.example settings.ini
```

2. Generate a new app at https://developer.spotify.com/my-applications

3. Fill in your `client_id` and `client_secret` from your Spotify app

4. For Google Play Music, open a console in the source code folder and run 

`python Setup.py <client>`

where `<client>` should be `mobileclient` to setup playlist transfers **or** `musicmanager` to be able to upload files with GoogleMusicManager.py.
For YouTube Music setup, use `youtube`.

Then, follow the command line instructions to grant this app access to your account. All credentials are stored locally in the file `settings.ini`. 

## Transfer a playlist

After you've created the settings file, you can simply run the script from the command line using:

`python GoogleMusic.py <spotifylink>`

where `<spotifylink>` is a link like https://open.spotify.com/user/edmsauce/playlist/3yGp845Tz2duWCORALQHFO
Alternatively you can also **use a file name** in place of a spotify link. The file should contain one song per line.

The script will log its progress and output songs that were not found in Google Play Music to **noresults.txt**.

## Transfer all playlists of a Spotify user

For migration purposes, it is possible to transfer all public playlists of a user by using the Spotify user's ID (unique username).

`python GoogleMusic.py --all <spotifyuserid>`

## Upload songs

To upload songs, run

`python GoogleMusicManager.py <filepath>`

## Command line options

There are some additional command line options for setting the playlist name and determining whether it's public or not. To view them, run

`> python GoogleMusic.py -h`

Arguments:

```
positional arguments:
  playlist              Provide a playlist Spotify link. Alternatively,
                        provide a text file (one song per line)

optional arguments:
  -h, --help            show this help message and exit
  -u UPDATE, --update UPDATE
                        Delete all entries in the provided Google Play Music
                        playlist and update the playlist with entries from the
                        Spotify playlist.
  -n NAME, --name NAME  Provide a name for the Google Play Music playlist.
                        Default: Spotify playlist name
  -i INFO, --info INFO  Provide description information for the Google Play
                        Music Playlist. Default: Spotify playlist description
  -d, --date            Append the current date to the playlist name
  -p, --public          Make the playlist public. Default: private
  -r, --remove          Remove playlists with specified regex pattern.
  -a, --all             Transfer all public playlists of the specified user
                        (Spotify User ID).
```
