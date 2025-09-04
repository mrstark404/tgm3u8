from flask import Flask, request, redirect
import yt_dlp

app = Flask(__name__)

@app.route('/')
def extract_m3u8():
    video_url = request.args.get('url')
    if not video_url:
        return "Please provide a 'url' parameter.", 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            # Look for an HLS (m3u8) format URL
            hls_url = next((f['url'] for f in info.get('formats', []) if '.m3u8' in f['url']), None)
            if hls_url:
                return redirect(hls_url)
            # Fallback to the main URL if it's an m3u8
            elif 'url' in info and '.m3u8' in info['url']:
                return redirect(info['url'])
            else:
                return "No m3u8 link found.", 404
        except Exception as e:
            return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
