# spotifyplaylist_to_gmusic
A simple script to clone a Spotify playlist to Google Play Music.

Initially you should create a new settings.ini containing your credentials for Google Play Music and Spotify.

For Google Play Music, get an app password from https://myaccount.google.com/apppasswords.

For Spotify, get your client_id and client_secret from https://developer.spotify.com/my-applications

After you've create the settings file, you can simply run the script from the command line using

`python GoogleMusic.py <spotifylink>`

where `<spotifylink>` is a link like https://open.spotify.com/user/edmsauce/playlist/3yGp845Tz2duWCORALQHFO


The script will log its progress and output songs that were not found in Google Play Music to **noresults.txt**.

