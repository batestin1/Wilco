import os
import requests
import json
import pandas as pd
import base64
from lyricsgenius import Genius
from tqdm import tqdm
import sys

data = open("/Users/mayconcyprianobatestin/Documents/repositorios/DATA_SCIENCE/MUSIC/secrets/secrets.json")
var = json.load(data)
client_id = var['client_id']
client_secret = var['client_secret']
genius_id = var['genius_id']

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
         "Authorization": "Basic " + auth_base64,
         "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    result = requests.post(url, headers=headers, data=data)
    final = json.loads(result.content)

    token = final['access_token']
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_id_artist(artist):
    url = f"https://api.spotify.com/v1/search?q={artist}&type=artist&limit=1"
    headers = get_auth_header(token)
    response = requests.get(url, headers=headers).json()
    return response['artists']['items'][0]['id']

def get_lyrics(artist, track_name):
    genius = Genius(genius_id)  
    song = genius.search_song(track_name, artist)
    if song:
        return song.lyrics
    else:
        return ''

artist = sys.argv[1:]
artist = " ".join(artist)
artist = artist.lower()
token = get_token()
id = get_id_artist(artist)

url = f"https://api.spotify.com/v1/artists/{id}/albums"
headers = get_auth_header(token)
response = requests.get(url, headers=headers).json()

artists = []
albums_ = []
tracklist = []
years = []
lyrics = []

for n in tqdm(range(len(response['items']))):
    album_name = response['items'][n]['name']
    album_year = response['items'][n]['release_date'][:4]
    album_id = response['items'][n]['id']
    
    tracks_url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    tracks_response = requests.get(tracks_url, headers=headers).json()
    
    for track in tracks_response['items']:
        artists.append(artist)
        albums_.append(album_name)
        tracklist.append(track['name'])
        years.append(album_year)
        lyrics.append(get_lyrics(artist, track['name']))

df = pd.DataFrame({
    'artist': artists,
    'album': albums_,
    'track': tracklist,
    'year': years,
    'lyrics': lyrics
})

artist = artist.replace(" ","_")
df.to_csv(f'/Users/mayconcyprianobatestin/Documents/repositorios/DATA_SCIENCE/MUSIC/dataset/dataset_{artist.lower()}.csv', index=False)
old_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')