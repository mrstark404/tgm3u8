from flask import Flask, request, redirect
from playwright.sync_api import sync_playwright
import re

app = Flask(__name__)

@app.route('/')
def fetch_m3u8():
    url = request.args.get('url')
    if not url:
        return "No URL provided", 400

    try:
        with sync_playwright() as p:
            # Launch headless Chromium
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            page = browser.new_page()
            page.goto(url, timeout=15000)  # 15s timeout
            html = page.content()
            browser.close()
    except Exception as e:
        return f"Error fetching page: {str(e)}", 500

    # Find any .m3u8 link
    match = re.search(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', html)
    if match:
        return redirect(match.group(0))
    else:
        return "No m3u8 link found", 404

if __name__ == "__main__":
    app.run(debug=True)
