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
        # Identify URL type
        if "spotify.com/track" in user_input:
            df = analyze_spotify_url(user_input)
            graph_title = "Spotify Track Metrics"

        elif "spotify.com/album" in user_input:
            df = analyze_spotify_album(user_input)
            graph_title = "Spotify Album Metrics"

        else:
            return jsonify({
                "type": "text",
                "message": "Please send a valid Spotify track or album URL."
            })

        # ----------------------
        # SAVE CSV PROPERLY
        # ----------------------
        csv_filename = f"spotify_data_{uuid.uuid4()}.csv"
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")

        # ----------------------
        # SAVE PNG PROPERLY
        # ----------------------
        img_buffer = io.BytesIO()

        width = max(11, len(df) * 0.8)
        height = 10

        plt.figure(figsize=(width, height))
        x = np.arange(len(df))

        plt.bar(x - 0.2, df["Popularity"], width=0.4, label="Popularity")
        plt.bar(x + 0.2, df["Duration (minutes)"], width=0.4, label="Duration (minutes)")

        plt.xticks(x, df["Track Name"], rotation=45, ha="right")
        plt.title(graph_title)
        plt.legend()
        plt.tight_layout()

        plt.savefig(img_buffer, format="png")
        plt.close()

        img_bytes = img_buffer.getvalue()  # << MUST USE THIS

        graph_filename = f"spotify_graph_{uuid.uuid4()}.png"

        # ----------------------
        # UPLOAD BOTH FILES CORRECTLY
        # ----------------------
        csv_url = asyncio.run(put(
            f"spotify_csv/{csv_filename}",
            csv_bytes,
            content_type="text/csv",
            access="public"
        ))

        graph_url = asyncio.run(put(
            f"spotify_graphs/{graph_filename}",
            img_bytes,
            content_type="image/png",
            access="public"
        ))

        # ----------------------
        # GENERATE HTML TABLE
        # ----------------------
        table_html = df.to_html(
            classes='table table-striped table-bordered',
            index=False
        )

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
