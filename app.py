from flask import Flask, request, redirect, abort
import requests
import re

app = Flask(__name__)

@app.route('/')
def fetch_m3u8():
    url = request.args.get('url')
    if not url:
        return "No URL provided", 400

    # Default headers to mimic a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": url
    }

    try:
        # Fetch the page with a session to handle cookies
        session = requests.Session()
        resp = session.get(url, headers=headers, timeout=10, allow_redirects=True)
        if resp.status_code != 200:
            return "Failed to fetch URL", 500
        html = resp.text
    except Exception as e:
        return f"Error: {str(e)}", 500

    # Regex to find .m3u8 links (both http and https)
    match = re.search(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', html)
    if match:
        m3u8_url = match.group(0)
        return redirect(m3u8_url)
    else:
        return "No m3u8 link found", 404

if __name__ == "__main__":
    app.run(debug=True)
