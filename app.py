# app.py
from flask import Flask, request, redirect, abort
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def fetch_m3u8():
    video_url = request.args.get('url')
    if not video_url:
        return abort(400, description="Missing 'url' parameter. Usage: /?url=<video_url>")

    try:
        # Use yt-dlp to extract info without downloading
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best[protocol^=m3u8]',  # Prefer HLS (m3u8) formats
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            # Get the URL of the m3u8 manifest
            m3u8_url = info['url'] if 'url' in info else None

            if m3u8_url and m3u8_url.endswith('.m3u8'):
                return redirect(m3u8_url)
            else:
                return abort(404, description="No m3u8 link found for the provided URL.")
    except Exception as e:
        return abort(500, description=f"Error processing URL: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
