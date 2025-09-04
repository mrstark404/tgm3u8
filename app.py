# app.py
from flask import Flask, request, redirect, jsonify, abort
import yt_dlp
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def fetch_m3u8():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "Missing 'url' parameter. Usage: /?url=<video_url>"}), 400

    # yt-dlp options for robust extraction
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best[protocol^=m3u8]/best',  # Prefer m3u8, fallback to best available
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': video_url,
        },
        'extract_flat': True,  # Avoid downloading, just extract metadata
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            m3u8_url = None

            # Check for m3u8 in formats
            if 'formats' in info:
                for fmt in info.get('formats', []):
                    if fmt.get('protocol', '').startswith('m3u8'):
                        m3u8_url = fmt['url']
                        break
            elif 'url' in info and info['url'].endswith('.m3u8'):
                m3u8_url = info['url']

            if m3u8_url:
                logger.info(f"Found m3u8 URL: {m3u8_url}")
                return redirect(m3u8_url)
            else:
                logger.warning(f"No m3u8 link found for {video_url}")
                return jsonify({"error": "No m3u8 link found for the provided URL."}), 404
    except Exception as e:
        logger.error(f"Error processing {video_url}: {str(e)}")
        return jsonify({"error": f"Failed to process URL: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
