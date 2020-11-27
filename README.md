# Transfer a Spotify Playlist to Google Play Music
A simple command line script to clone a Spotify playlist to Google Play Music. 
Also includes interfaces for 
- creating a Play Music playlist from a text file
- uploading local MP3s to Play Music

**New:** YouTube Music support. Spotify playlists can now be transferred to YouTube Music thanks to [ytmusicapi](https://github.com/sigma67/ytmusicapi).
Usage is identical to GoogleMusic.py, just use `python YouTube.py` with the same parameters.

## Requirements

- Python 3 - https://www.python.org
- Python extensions: `pip install -U -r requirements`

## Setup

Initially you should create a new settings.ini containing your Spotify credentials. Simply copy settings.ini.example to a new file settings.ini and fill in your client_id and client_secret from https://developer.spotify.com/my-applications

For Google Play Music, open a console in the source code folder and run this script. Then follow the command line instructions to grant the app access to your account. All credentials are stored locally in the file `settings.ini`.

### Google Play Music upload

`python Setup.py --musicmanager`

### Google Play Music playlist transfers

`python Setup.py --mobileclient`

### YouTube Music playlist transfers
`python Setup.py --youtube`

> Then YTMusic will ask for the request header of https://music.youtube.com/browse

[YTMusic's Document](https://ytmusicapi.readthedocs.io/en/latest/setup.html#copy-authentication-headers)

Or passing raw headers as the 2nd argument.

`python Setup.py --youtube --headers_raw "HEADERS"`

## Transfer playlists

After you've created the settings file, you can simply run the script from the command line using

`python GoogleMusic.py <spotifylink>`

where `<spotifylink>` is a link like https://open.spotify.com/user/edmsauce/playlist/3yGp845Tz2duWCORALQHFO
Alternatively you can also **use a file name** in place of a spotify link. The file should contain one song per line.

The script will log its progress and output songs that were not found in Google Play Music to **noresults.txt**.

## Transfer all playlists of a user
For migration purposes, it is possible to transfer all public playlists of a user by using the user's ID (unique username). 

`python GoogleMusic.py --all <user>`

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

## Batch playlists transfers to Youtube in single script (You can skip the Setup.py)

1) Update Spotify's credentials  `client_id` and `client_secret` in `setting.ini` file.
2) Prepare list of Spotify's playlists `spotify_playlists.txt` please check `spotify_playlists.txt.example` for the example.
3) Prepare the headers `youtube_headers_raw.txt` please check `youtube_headers_raw.txt.example` for the example. [YTMusic's Document](https://ytmusicapi.readthedocs.io/en/latest/setup.html#copy-authentication-headers)

> Incase you want to create playlist using brand account. You've to update `user_id` in `setting.ini` file. Otherwise just leave it blank.

> You can retrieve the user ID by going to https://myaccount.google.com/brandaccounts and selecting your brand account. The user ID will be in the URL: https://myaccount.google.com/b/user_id/

4) Run the script. `python SpotifyToYoutube.py`
> By default, it will upload as private playlist using name and info from Spotify.

```
Transfer spotify playlist to YouTube Music.

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Provide a name for the YouTube Music playlist. Default: Spotify playlist name
  -i INFO, --info INFO  Provide description information for the YouTube Music Playlist. Default: Spotify playlist description
  -d, --date            Append the current date to the playlist name
  -p, --public          Make the playlist public. Default: private
  -r, --remove          Remove playlists with specified regex pattern.
  -a, --all             Transfer all public playlists of the specified user (Spotify User ID).
```