`Song_analyzer`
  
    ```A web-based Flask app that analyzes Spotify tracks and albums. It retrieves information such as track name, artist, album, popularity, and duration, and displays it through interactive charts.```

**Spotify Analyzer Chatbot (Flask + Matplotlib) :**

  This project is an interactive Spotify Track \& Album Analyzer built with Python Flask, Spotipy API, and Matplotlib.
  
  Users can paste a Spotify track or album URL, and the chatbot automatically:

  Fetches track/album data (popularity, duration, etc.)

  Displays it in a Bootstrap-styled table

  Generates a graph visualization

  Allows you to download both the graph (PNG) and table (CSV)

  Shows a cool animated loading GIF while analyzing 


**Features :**



✅ Spotify Track \& Album Analysis :

  Enter any valid Spotify track or album link.

  Automatically retrieves metadata like track name, artist, popularity, and duration.


✅ Visual Graph Generation :

  Generates a Matplotlib bar chart showing “Popularity” vs “Duration (minutes)”.

  Saves the graph as a PNG and displays it dynamically in chat.


✅ Download Options :

  "Download CSV file of the analysis table."

  "Download PNG file of the generated graph."


✅ Interactive Chat UI :

  Built using Bootstrap 5 and custom CSS.

  Real-time chat simulation with bot and user messages.


✅ Loading Animation :

  A “Sound Waves” GIF loader appears when the analysis is processing.

  Smoothly transitions into results display after 3 seconds.



**Folder Structure :**


Song_Analyzer
│
├── app.py
├── spotify_analyser.py
├── requirements.txt
│
├── static/
│     ├── style.css
│     ├── graphs/
│     │     └── Graph_data
│     ├── images/
│     │     └── SoundWaves
│     └── downloads/
│           └── Tables_data
│
├── README/
│
└── templates/
      └── index.html


**Installation & Setup :**


Clone the repository :

    git clone https://github.com/yourusername/spotify-analyzer-chatbot.git
    cd spotify-analyzer-chatbot


Install dependencies :

    pip install -r requirements.txt

Set Spotify API credentials :

Get your Spotify Client ID and Client Secret from,
        https://developer.spotify.com/dashboard

Then set them as environment variables,

    set SPOTIPY_CLIENT_ID="your_client_id"
    set SPOTIPY_CLIENT_SECRET="your_client_secret"

Run the Flask server :

    python app.py

Open your browser and Go to,
    
    http://127.0.0.1:5000

**Future Enhancements :**

  Support for playlist analysis
  Sentiment analysis of song lyrics 🎶
  Integrate with Spotify authentication for personalized analytics
  Responsive dark/light theme toggle

**Author :**

Developed by: Vikhash .T
📬 For feedback or suggestions — feel free to reach out at, https://vikhash-portfolio.vercel.app/#edu

**License :**

This project is licensed under the MIT License.
You are free to use, modify, and distribute it for educational and non-commercial purposes.

