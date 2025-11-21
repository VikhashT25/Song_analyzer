# app.py
import os
import uuid
import io
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify
from spotify_analyser import analyze_spotify_url, analyze_spotify_album
from vercel_blob import put
import asyncio
import pandas as pd

matplotlib.use('Agg')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').strip()

    try:
        if "spotify.com/track" in user_input:
            df = analyze_spotify_url(user_input)
            graph_title = "Spotify Track Metrics"

        elif "spotify.com/album" in user_input:
            df = analyze_spotify_album(user_input)
            graph_title = "Spotify Album Metrics"

        else:
            return jsonify({"type": "text", "message": "Invalid Spotify URL."})

        # -------------------- CSV --------------------
        csv_filename = f"spotify_{uuid.uuid4()}.csv"
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")

        # -------------------- PNG --------------------
        img_filename = f"spotify_graph_{uuid.uuid4()}.png"
        img_buffer = io.BytesIO()

        plt.figure(figsize=(12, 6))
        plt.bar(df.index - 0.2, df["Popularity"], width=0.4, label="Popularity")
        plt.bar(df.index + 0.2, df["Duration (minutes)"], width=0.4, label="Duration (minutes)")
        plt.xticks(df.index, df["Track Name"], rotation=45, ha="right")
        plt.tight_layout()
        plt.legend()

        plt.savefig(img_buffer, format="png")
        plt.close()

        img_bytes = img_buffer.getvalue()  # CORRECT — use ONLY getvalue()

        # -------------------- Upload --------------------
        csv_url = asyncio.run(put(f"spotify_csv/{csv_filename}", csv_bytes, "text/csv"))
        png_url = asyncio.run(put(f"spotify_graphs/{img_filename}", img_bytes, "image/png"))

        return jsonify({
            "type": "spotify_analysis",
            "table": df.to_html(classes="table table-striped", index=False),
            "download_csv": csv_url,
            "graph_url": png_url
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
