from flask import Flask, request, redirect, send_file
import yt_dlp
import ffmpeg
import logging
import os
import tempfile
import uuid
from urllib.parse import urlparse

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def extract_m3u8():
    video_url = request.args.get('url')
    download = request.args.get('download', 'false').lower() == 'true'

    if not video_url:
        return "Please provide a 'url' parameter.", 400

    # yt-dlp options for extraction
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': video_url,
        },
        'extract_flat': True,  # Extract metadata without downloading
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            logger.info(f"Extracting info from: {video_url}")
            info = ydl.extract_info(video_url, download=False)

            # Look for m3u8 or blob URLs
            hls_url = None
            for f in info.get('formats', []):
                if f.get('url') and '.m3u8' in f['url']:
                    hls_url = f['url']
                    break
            if not hls_url and 'url' in info and '.m3u8' in info['url']:
                hls_url = info['url']
            elif not hls_url and 'url' in info and 'blob:' in info['url']:
                logger.warning("Blob URL detected, attempting recording mode simulation.")
                # Simulate FetchV's recording mode by forcing a direct stream capture
                ydl_opts['format'] = 'best'
                ydl_opts['extract_flat'] = False
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    hls_url = info.get('url')

            if not hls_url:
                logger.warning("No m3u8 or usable URL found.")
                return "No m3u8 link found.", 404

            logger.info(f"Found URL: {hls_url}")

            if download:
                # Download and merge into MP4
                temp_dir = tempfile.mkdtemp()
                output_file = os.path.join(temp_dir, f"video_{uuid.uuid4().hex}.mp4")
                try:
                    logger.info("Starting download and conversion to MP4...")
                    stream = ffmpeg.input(hls_url)
                    stream = ffmpeg.output(stream, output_file, c='copy', f='mp4', loglevel='error')
                    ffmpeg.run(stream)
                    filename = os.path.basename(urlparse(video_url).path) + '.mp4'
                    return send_file(output_file, as_attachment=True, download_name=filename)
                except Exception as e:
                    logger.error(f"FFmpeg error: {str(e)}")
                    return f"Error processing video: {str(e)}", 500
                finally:
                    if os.path.exists(output_file):
                        os.remove(output_file)
                        os.rmdir(temp_dir)
            else:
                # Redirect to m3u8 URL
                return redirect(hls_url)

        except Exception as e:
            logger.error(f"Error extracting info: {str(e)}")
            return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
