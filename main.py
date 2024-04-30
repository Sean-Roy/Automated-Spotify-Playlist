import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint

BILLBOARD_ENDPOINT = "https://www.billboard.com/charts/hot-100/"

# API & Token information:
# Spotify: https://developer.spotify.com/
# TODO: Use your own Spotify Client ID & Secret keys.
SPOTIFY_CLIENTID = "INSERT_YOUR_CLIENT_ID"
SPOTIFY_SECRET = "INSERT_YOUR_SPOTIFY_SECRET"
# TODO: Can use your own link or local host.
# SPOTIFY_REDIRECT = "http://example.com"  # did not work - returned DNS error
SPOTIFY_REDIRECT = "http://127.0.0.1:9090"  # using local host since example.com results in DNS error
# TODO: Use your own Spotify profile name.
SPOTIFY_DISPLAY = "INSERT_YOUR_OWN_SPOTIFY_PROFILE"

# Ask the user for the desired date:
date = input("Which year do you want to time-travel to? Type the date in YYYY-MM-DD format: ")
# date = "2000-08-12"  # For testing purposes
year = date[:4]
# print(year)

# Grab the Top 100 songs from the Billboard site:
response = requests.get(BILLBOARD_ENDPOINT + f"{date}")
bb_website = response.text
# print(bb_website)

soup = BeautifulSoup(bb_website, "html.parser")
# print(soup.title)
song_titles = soup.select("li ul li h3")
# print(song_titles)
song_list = [song.getText().strip() for song in song_titles]
# print(song_list)

# Connect to Spotify:
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENTID,
        client_secret=SPOTIFY_SECRET,
        redirect_uri=SPOTIFY_REDIRECT,
        scope="playlist-modify-private",
        cache_path="token.txt",
        username=SPOTIFY_DISPLAY,
        show_dialog=True,
    )
)
# pprint(sp.current_user())
user_id = sp.current_user()["id"]
# print(user_id)

# Search for the identified songs in spotify:
# test_song = song_list[0]  # Test song used to figure out path for uri from search
# print(test_song)
song_uris = []
for song in song_list:
    query = f"track:{song} year:{year}"
    search = sp.search(q=query, type="track")
    # pprint(search["tracks"]["items"][0]["uri"])
    try:
        uri = search["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify - skipped!")

# Create a new playlist to add the songs to:
new_playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False,
                                       description=f"Top 100 songs from {year}.")
# pprint(new_playlist)
playlist_id = new_playlist["id"]
# print(playlist_id)

# Add the found songs to the playlist:
playlist = sp.playlist_add_items(playlist_id=playlist_id, items=song_uris)
