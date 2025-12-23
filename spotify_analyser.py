import os
import pandas as pd
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise ValueError("Missing Spotify credentials")

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

def extract_id(url: str):
    """Extracts 22-char Spotify ID from any valid Spotify link."""
    for part in url.split("/"):
        if "?" in part:
            part = part.split("?")[0]
        if len(part) == 22:
            return part
    raise ValueError("Invalid Spotify URL")


def analyze_spotify_url(track_url):
    try:
        track_id = extract_id(track_url)
        track = sp.track(track_id)

        data = {
            "Track Name": [track["name"]],
            "Artist": [track["artists"][0]["name"]],
            "Album": [track["album"]["name"]],
            "Popularity": [track["popularity"]],
            "Duration (minutes)": [round(track["duration_ms"] / 60000, 2)]
        }

        return pd.DataFrame(data)

    except Exception as e:
        raise Exception(f"Error analyzing track: {str(e)}")


def analyze_spotify_album(album_url):
    try:
        album_id = extract_id(album_url)
        album = sp.album(album_id)
        tracks = sp.album_tracks(album_id)

        track_ids = [t["id"] for t in tracks["items"]]
        track_info_list = sp.tracks(track_ids)["tracks"]  # batch fetch

        rows = [
            {
                "Track Name": t["name"],
                "Artist": t["artists"][0]["name"],
                "Album": album["name"],
                "Popularity": t["popularity"],
                "Duration (minutes)": round(t["duration_ms"] / 60000, 2),
            }
            for t in track_info_list
        ]

        return pd.DataFrame(rows)

    except Exception as e:
        raise Exception(f"Error analyzing album: {str(e)}")
