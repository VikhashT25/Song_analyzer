import os
import uuid
import io
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify
from spotify_analyser import analyze_spotify_url, analyze_spotify_album
from vercel_blob import put  # ✅ You’ll create this helper (shown below)
import asyncio
import pandas as pd

matplotlib.use('Agg')

app = Flask(__name__)

# ✅ ROUTE: Homepage
@app.route('/')
def index():
    return render_template('index.html')


# ✅ ROUTE: Spotify Analyzer
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').strip()

    try:
        # --- 🎵 Track URL ---
        if "spotify.com/track" in user_input:
            df = analyze_spotify_url(user_input)
            graph_title = "Spotify Track Metrics"

        # --- 💿 Album URL ---
        elif "spotify.com/album" in user_input:
            df = analyze_spotify_album(user_input)
            graph_title = "Spotify Album Metrics"

        else:
            return jsonify({
                "type": "text",
                "message": "Please send a Spotify track or album URL."
            })

        # ✅ Convert DataFrame to CSV (in-memory)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        # ✅ Generate Graph (in-memory)
        img_buffer = io.BytesIO()
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
        plt.title(graph_title, fontsize=20, fontweight='bold')
        plt.xticks(ticks=x, labels=labels, rotation=45, ha='right')
        plt.tight_layout()
        plt.legend()
        plt.savefig(img_buffer, format='png')
        plt.close()
        img_buffer.seek(0)

        # ✅ Upload both to Vercel Blob
        csv_filename = f"{uuid.uuid4().hex}.csv"
        graph_filename = f"{uuid.uuid4().hex}.png"

        csv_url = asyncio.run(put(f"spotify_csv/{csv_filename}", csv_buffer.getvalue(), "text/csv"))
        graph_url = asyncio.run(put(f"spotify_graphs/{graph_filename}", img_buffer.read(), "image/png"))

        # ✅ Convert DataFrame to HTML
        table_html = df.to_html(classes='table table-striped table-bordered', index=False)

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
