import os
import pandas as pd
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import os
print("VERCEL_BLOB_READ_WRITE_TOKEN:", bool(os.getenv("VERCEL_BLOB_READ_WRITE_TOKEN")))


# ✅ Load environment variables from .env file
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

print("CLIENT_ID loaded:", bool(SPOTIFY_CLIENT_ID))

# ✅ Initialize Spotify API client
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise ValueError("Missing Spotify API credentials. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# =====================================================
# 🎵 Function: Analyze a single track URL
# =====================================================
def analyze_spotify_url(track_url):
    """Analyzes a single Spotify track and returns a pandas DataFrame."""
    try:
        track_id = track_url.split("/")[-1].split("?")[0]
        track = sp.track(track_id)

        track_data = {
            'Track Name': [track['name']],
            'Artist': [track['artists'][0]['name']],
            'Album': [track['album']['name']],
            'Popularity': [track['popularity']],
            'Duration (minutes)': [round(track['duration_ms'] / 60000, 2)]
        }

        return pd.DataFrame(track_data)

    except Exception as e:
        raise Exception(f"Error analyzing track: {str(e)}")


# =====================================================
# 💿 Function: Analyze an album URL
# =====================================================
def analyze_spotify_album(album_url):
    """Analyzes all tracks in a Spotify album and returns a pandas DataFrame."""
    try:
        album_id = album_url.split("/")[-1].split("?")[0]
        album = sp.album(album_id)
        tracks = sp.album_tracks(album_id)

        track_data = []
        for track in tracks['items']:
            track_info = sp.track(track['id'])
            track_data.append({
                'Track Name': track_info['name'],
                'Artist': track_info['artists'][0]['name'],
                'Album': album['name'],
                'Popularity': track_info['popularity'],
                'Duration (minutes)': round(track_info['duration_ms'] / 60000, 2)
            })

        return pd.DataFrame(track_data)

    except Exception as e:
        raise Exception(f"Error analyzing album: {str(e)}")
