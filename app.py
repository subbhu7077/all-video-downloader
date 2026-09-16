import re
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def api_download():
    payload = request.get_json() or {}
    url = payload.get('url', '').strip()

    if not url:
        return jsonify({'success': False, 'error': 'Kripya kisi video ka URL enter karein.'}), 400

    # Universal extractor options
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title') or 'Social Media Video'
            thumb = info.get('thumbnail') or ''
            direct_video = info.get('url') or ''
            audio_url = direct_video
            server2 = direct_video

            formats = info.get('formats', [])
            
            # Format sorting for HD, SD and Pure Audio
            for f in formats:
                # Direct audio stream
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('url'):
                    audio_url = f.get('url')
                # Server 2 backup MP4
                if f.get('ext') == 'mp4' and f.get('url'):
                    server2 = f.get('url')

            if not direct_video and formats:
                direct_video = formats[-1].get('url', '')

            return jsonify({
                'success': True,
                'title': title,
                'thumbnail': thumb,
                'download_hd': direct_video,
                'download_server2': server2,
                'download_mp3': audio_url
            })

    except Exception as e:
        return jsonify({'success': False, 'error': 'Link fetch nahi ho paya. URL check karein ki wo public video hai ya nahi.'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
