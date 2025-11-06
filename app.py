from flask import Flask, render_template, request, jsonify
import os
import uuid
import io
import requests
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from spotify_analyser import analyze_spotify_url, analyze_spotify_album

# Configure Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/graphs'

# Use non-interactive backend for Matplotlib
matplotlib.use('Agg')


# ==========================
# 🎯 Upload helper functions
# ==========================

def upload_to_vercel_blob(filename, content_bytes, content_type="text/csv"):
    """Uploads a file (CSV or PNG) to Vercel Blob Storage and returns its public URL."""
    blob_url = "https://api.vercel.com/v2/blob"
    token = os.getenv("VERCEL_BLOB_READ_WRITE_TOKEN")

    if not token:
        raise ValueError("Missing VERCEL_BLOB_READ_WRITE_TOKEN environment variable.")

    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": (filename, content_bytes, content_type)}

    response = requests.post(blob_url, headers=headers, files=files)
    response.raise_for_status()
    return response.json()["url"]


# ==========================
# 🧠 Main Routes
# ==========================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').strip()

    try:
        # --- 🎵 Handle Track URL ---
        if "spotify.com/track" in user_input:
            df = analyze_spotify_url(user_input)
            graph_title = "Spotify Track Metrics"

        # --- 💿 Handle Album URL ---
        elif "spotify.com/album" in user_input:
            df = analyze_spotify_album(user_input)
            graph_title = "Spotify Album Metrics"

        else:
            return jsonify({
                "type": "text",
                "message": "Please send a Spotify track or album URL (e.g., https://open.spotify.com/track/... or /album/...)."
            })

        # ✅ Convert to HTML table
        table_html = df.to_html(classes='table table-striped table-bordered', index=False)

        # ==========================
        # 📊 Upload CSV to Blob
        # ==========================
        csv_filename = f"{uuid.uuid4().hex}.csv"

        csv_bytes = io.BytesIO()
        df.to_csv(csv_bytes, index=False)
        csv_bytes.seek(0)
        csv_url = upload_to_vercel_blob(csv_filename, csv_bytes, "text/csv")

        # ==========================
        # 📈 Generate Graph
        # ==========================
        graph_filename = f"{uuid.uuid4().hex}.png"
        graph_bytes = io.BytesIO()

        width = max(11, len(df) * 0.8)
        height = 10
        plt.figure(figsize=(width, height))

        labels = df['Track Name']
        popularity = df['Popularity']
        duration = df['Duration (minutes)']

        x = np.arange(len(labels))
        bar_width = 0.35
        gap = 0.1

        plt.bar(x - bar_width/2 - gap/2, popularity, width=bar_width, label='Popularity')
        plt.bar(x + bar_width/2 + gap/2, duration, width=bar_width, label='Duration (minutes)')
        plt.title(graph_title, fontsize=18, fontweight='bold')
        plt.xticks(ticks=x, labels=labels, rotation=45, ha='right')
        plt.tight_layout()
        plt.legend()
        plt.savefig(graph_bytes, format='png')
        plt.close()

        graph_bytes.seek(0)
        graph_url = upload_to_vercel_blob(graph_filename, graph_bytes, "image/png")

        # ✅ Return JSON Response
        return jsonify({
            "type": "spotify_analysis",
            "table": table_html,
            "download_csv": csv_url,
            "graph_url": graph_url
        })

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(debug=True)
