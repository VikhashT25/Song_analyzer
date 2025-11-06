import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
print("Looking for .env file at:", dotenv_path)

load_dotenv(dotenv_path)
print("SPOTIFY_CLIENT_ID:", os.getenv("SPOTIFY_CLIENT_ID"))
