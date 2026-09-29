import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, template_folder='templates')
CORS(app)

# ── 1. アクセスしたときにフロント画面（HTML）を表示する設定 ──
@app.route('/')
def index():
    return render_template('index.html')

# ── 2. 音声URLを取得するAPI ──
@app.route('/get_audio', methods=['GET'])
def get_audio():
    playlist_url = request.args.get('playlist')
    index = request.args.get('index', default=0, type=int)

    if not playlist_url:
        return jsonify({"error": "プレイリストURLが必要です"}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'extract_flat': 'in_playlist',
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            
            if 'entries' not in playlist_info or not playlist_info['entries']:
                return jsonify({"error": "動画が見つかりません。URLが正しいか、または非公開でないか確認してください。"}), 404
            
            entries = list(playlist_info['entries'])
            total_videos = len(entries)

            if index >= total_videos or index < 0:
                index = 0

            target_video = entries[index]
            video_url = f"https://youtube.com{target_video['id']}"
            
            with yt_dlp.YoutubeDL({'format': 'bestaudio/best', 'skip_download': True}) as ydl_single:
                video_info = ydl_single.extract_info(video_url, download=False)
                audio_url = video_info['url']
                title = video_info.get('title', 'Unknown Title')

            return jsonify({
                "audio_url": audio_url,
                "title": title,
                "next_index": (index + 1) % total_videos,
                "total": total_videos
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
