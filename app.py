# app.py
import io
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from dotenv import load_dotenv
load_dotenv()


from spotify_analyser import analyze_spotify_url, analyze_spotify_album

matplotlib.use('Agg')

app = Flask(__name__)

# -------------------------------
# Home
# -------------------------------
@app.route('/')
def index():
    return render_template('index.html')


# -------------------------------
# Chat Route (ANALYSIS ONLY)
# -------------------------------
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

        # ✅ Store data in memory (safe for streaming)
        app.config["LAST_DF"] = df
        app.config["GRAPH_TITLE"] = graph_title

        # ✅ Generate HTML table
        table_html = df.to_html(
            classes='table table-striped table-bordered',
            index=False
        )

        return jsonify({
            "type": "spotify_analysis",
            "table": table_html
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# -------------------------------
# CSV DOWNLOAD
# -------------------------------
@app.route('/download/csv')
def download_csv():
    df = app.config.get("LAST_DF")

    if df is None:
        return "No data available", 400

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return send_file(
        io.BytesIO(buffer.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="spotify_analysis.csv"
    )


# -------------------------------
# PNG DOWNLOAD
# -------------------------------
@app.route('/download/graph')
def download_graph():
    df = app.config.get("LAST_DF")
    title = app.config.get("GRAPH_TITLE")

    if df is None:
        return "No data available", 400

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

    plt.title(title, fontsize=18, fontweight='bold')
    plt.xticks(x, labels, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()

    plt.savefig(img_buffer, format="png")
    plt.close()
    img_buffer.seek(0)

    return send_file(
        img_buffer,
        mimetype="image/png",
        as_attachment=True,
        download_name="spotify_graph.png"
    )


if __name__ == '__main__':
    app.run(debug=True)
