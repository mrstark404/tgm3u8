import os
import math
from flask import Flask, Response
from pyrogram import Client

API_ID = int(os.getenv("27490071"))
API_HASH = os.getenv("b30b04232ede5e12b7891976f4f1df6e")
BOT_TOKEN = os.getenv("8454723419:AAEsYdkVnJPvH_5u9W_-6Z6Mc7YXs-j6z_Q")
CHANNEL_ID = int(os.getenv("-1002907246210"))
SEGMENT_SIZE = 5 * 1024 * 1024  # 5 MB chunks

tg = Client("stream_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
app = Flask(__name__)

@app.route("/stream/<int:message_id>/master.m3u8")
def master_playlist(message_id):
    with tg:
        msg = tg.get_messages(CHANNEL_ID, message_id)
        file = msg.video or msg.document
        if not file:
            return "No video found", 404

        file_size = file.file_size
        total_segments = math.ceil(file_size / SEGMENT_SIZE)

        playlist = "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:10\n#EXT-X-MEDIA-SEQUENCE:0\n"
        for i in range(total_segments):
            playlist += f"#EXTINF:10.0,\n/stream/{message_id}/segment/{i}\n"
        playlist += "#EXT-X-ENDLIST\n"

        return Response(playlist, mimetype="application/vnd.apple.mpegurl")

@app.route("/stream/<int:message_id>/segment/<int:seg_id>")
def stream_segment(message_id, seg_id):
    with tg:
        msg = tg.get_messages(CHANNEL_ID, message_id)
        file = msg.video or msg.document
        if not file:
            return "No video", 404

        file_size = file.file_size
        file_id = file.file_id
        total_segments = math.ceil(file_size / SEGMENT_SIZE)

        if seg_id >= total_segments:
            return "Segment not found", 404

        start = seg_id * SEGMENT_SIZE
        end = min(start + SEGMENT_SIZE - 1, file_size - 1)

        def generate():
            for chunk in tg.stream_media(file_id, offset=start, limit=(end - start + 1)):
                yield chunk

        return Response(generate(), mimetype="video/MP2T")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
