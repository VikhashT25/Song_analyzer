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
        # 🎵 Track URL
        if "spotify.com/track" in user_input:
            df = analyze_spotify_url(user_input)
            graph_title = "Spotify Track Metrics"

        # 💿 Album URL
        elif "spotify.com/album" in user_input:
            df = analyze_spotify_album(user_input)
            graph_title = "Spotify Album Metrics"

        else:
            return jsonify({
                "type": "text",
                "message": "Please send a valid Spotify track or album URL."
            })

        
        
        # --- Convert CSV & PNG to bytes properly ---
        csv_bytes = csv_buffer.getvalue().encode("utf-8")
        img_bytes = img_buffer.getvalue()



        # ✅ Create Graph (PNG)
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
        img_bytes = img_buffer.getvalue()

        # --- Upload both to Vercel Blob ---
        csv_bytes = csv_buffer.getvalue().encode("utf-8")
        img_bytes = img_buffer.getvalue()
        
        csv_url = asyncio.run(put(f"spotify_csv/{csv_filename}", csv_buffer.getvalue(), "text/csv"))
        graph_url = asyncio.run(put(f"spotify_graphs/{graph_filename}", img_buffer.read(), "image/png"))


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

        # ✅ Generate HTML table
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
