# app.py
from flask import Flask, render_template, request, jsonify
import os
import uuid
import matplotlib
import matplotlib.pyplot as plt
from spotify_analyser import analyze_spotify_url, analyze_spotify_album
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/graphs'
app.config['DOWNLOAD_FOLDER'] = 'static/downloads'

@app.route('/')
def index():
    return render_template('index.html')

matplotlib.use('Agg')

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
        csv_filename = f"{uuid.uuid4().hex}.csv"
        csv_path = f"static/downloads/{filename}.csv"
        df.to_csv(csv_path, index=False)ex=False)
        

        # ✅ Generate graph
        graph_filename = f"{uuid.uuid4().hex}.png"
        graph_path = os.path.join(app.config['UPLOAD_FOLDER'], graph_filename)

        # Dynamic resizing based on number of tracks
        width = max(11, len(df) * 0.8)  # Minimum width 8, adds 0.8 per track
        height = 10
        plt.figure(figsize=(width, height))

        labels = df['Track Name']
        popularity = df['Popularity']
        duration = df['Duration (minutes)']

        x = np.arange(len(labels))
        width = 0.35
        gap = 0.1

        plt.bar(x - width/2 - gap/2, popularity, width=width, label='Popularity')
        plt.bar(x + width/2 + gap/2, duration, width=width, label='Duration (minutes)')

        plt.title(graph_title, fontsize=20, fontweight='bold')
        plt.xticks(ticks=x, labels=labels, rotation=45, ha='right')
        plt.tight_layout()
        plt.legend()
        plt.savefig(graph_path)
        plt.close()

        # ✅ Return response
        return jsonify({
            "type": "spotify_analysis",
            "table": table_html,
            "download_csv": f"/static/downloads/{csv_filename}",
            "graph_url": f"/static/graphs/{graph_filename}"
        })

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    """Serve CSV downloads."""
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)



if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
