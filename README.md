# spotifyplaylist_to_gmusic
A simple script to clone a Spotify playlist to Google Play Music.

Initially you should create a new settings.ini containing your Spotify credentials. Simply copy settings.ini.example to a new file settings.ini and fill in your client_id and client_secret from https://developer.spotify.com/my-applications

For Google Play Music, run 

`python Setup.py <client>`

and follow the command line instructions to grant the app access to your account. All credentials are stored locally in the file `settings.ini`. 

Replace `<client>` with `mobileclient` to setup playlist transfers. Replace with `musicmanager` to be able to upload files with GoogleMusicManager.py.

After you've created the settings file, you can simply run the script from the command line using

`python GoogleMusic.py <spotifylink>`

where `<spotifylink>` is a link like https://open.spotify.com/user/edmsauce/playlist/3yGp845Tz2duWCORALQHFO

The script will log its progress and output songs that were not found in Google Play Music to **noresults.txt**.


To upload songs, run

`python GoogleMusic.py <filepath>`