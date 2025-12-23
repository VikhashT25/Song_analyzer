# app.py
import io
import uuid
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from dotenv import load_dotenv

from spotify_analyser import analyze_spotify_url, analyze_spotify_album

load_dotenv()
matplotlib.use('Agg')

app = Flask(__name__)

# --------------------------------
# In-memory file store (safe & fast)
# --------------------------------
FILE_STORE = {}

# --------------------------------
# Home
# --------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# --------------------------------
# Chat Route
# --------------------------------
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').strip()

    try:
        # 🎵 Track
        if "spotify.com/track" in user_input:
            df = analyze_spotify_url(user_input)
            graph_title = "Spotify Track Metrics"

        # 💿 Album
        elif "spotify.com/album" in user_input:
            df = analyze_spotify_album(user_input)
            graph_title = "Spotify Album Metrics"

        else:
            return jsonify({
                "type": "text",
                "message": "Please send a valid Spotify track or album URL."
            })

        # ---------------- CSV ----------------
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")

        # ---------------- PNG ----------------
        img_buffer = io.BytesIO()
        width = max(11, len(df) * 0.8)
        plt.figure(figsize=(width, 10))

        labels = df['Track Name']
        popularity = df['Popularity']
        duration = df['Duration (minutes)']

        x = np.arange(len(labels))
        bar_width = 0.35

        plt.bar(x - bar_width / 2, popularity, width=bar_width, label='Popularity')
        plt.bar(x + bar_width / 2, duration, width=bar_width, label='Duration')

        plt.title(graph_title, fontsize=18, fontweight='bold')
        plt.xticks(x, labels, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()

        plt.savefig(img_buffer, format="png")
        plt.close()

        img_bytes = img_buffer.getvalue()

        # ---------------- Store files ----------------
        file_id = uuid.uuid4().hex
        FILE_STORE[file_id] = {
            "csv": csv_bytes,
            "png": img_bytes
        }

        # ---------------- Response ----------------
        return jsonify({
            "type": "spotify_analysis",
            "table": df.to_html(classes='table table-striped table-bordered', index=False),
            "download_csv": f"/download/csv/{file_id}",
            "graph_url": f"/download/png/{file_id}"
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# --------------------------------
# CSV Download
# --------------------------------
@app.route('/download/csv/<file_id>')
def download_csv(file_id):
    if file_id not in FILE_STORE:
        return "File not found", 404

    return send_file(
        io.BytesIO(FILE_STORE[file_id]["csv"]),
        mimetype="text/csv",
        as_attachment=True,
        download_name="spotify_analysis.csv"
    )

# --------------------------------
# PNG Download
# --------------------------------
@app.route('/download/png/<file_id>')
def download_png(file_id):
    if file_id not in FILE_STORE:
        return "File not found", 404

    return send_file(
        io.BytesIO(FILE_STORE[file_id]["png"]),
        mimetype="image/png",
        as_attachment=True,
        download_name="spotify_graph.png"
    )

# --------------------------------
# Run
# --------------------------------
if __name__ == "__main__":
    app.run(debug=True)
