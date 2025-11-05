import os
import re
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials

# --- Spotify API Setup ---
# Option 1: Directly include credentials (for local testing only)
 
    
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")         # ← Replace this with your client_id
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")        # ← Replace this with your secret key


# ✅ Function 1: Analyze a single Spotify track
def analyze_spotify_url(track_url):
    try:
        # Extract track ID from URL
        track_id = re.search(r'track/([a-zA-Z0-9]+)', track_url).group(1)
        track = sp.track(track_id)

        # Extract details
        track_data = {
            'Track Name': [track['name']],
            'Artist': [track['artists'][0]['name']],
            'Album': [track['album']['name']],
            'Popularity': [track['popularity']],
            'Duration (minutes)': [round(track['duration_ms'] / 60000, 2)]
        }

        df = pd.DataFrame(track_data)
        return df

    except Exception as e:
        raise Exception(f"Error analyzing track: {e}")

# ✅ Function 2: Analyze an entire album
def analyze_spotify_album(album_url):
    try:
        # Extract album ID
        album_id = re.search(r'album/([a-zA-Z0-9]+)', album_url).group(1)
        album = sp.album(album_id)
        tracks = sp.album_tracks(album_id)

        album_name = album['name']
        artist_name = album['artists'][0]['name']

        data = []
        for track in tracks['items']:
            details = sp.track(track['id'])
            data.append({
                'Track Name': details['name'],
                'Artist': artist_name,
                'Album': album_name,
                'Popularity': details['popularity'],
                'Duration (minutes)': round(details['duration_ms'] / 60000, 2)
            })

        df = pd.DataFrame(data)
        return df

    except Exception as e:
        raise Exception(f"Error analyzing album: {e}")
    
