from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

SITE_URL = "https://all-video-downloader-qc9k.onrender.com"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sw.js')
def service_worker():
    sw_code = """Self.options = {
    "domain": "3nbf4.com",
    "zoneId": 11819847
}
self.lary = ""
importScripts('https://3nbf4.com/act/files/service-worker.min.js?r=sw')"""
    return Response(sw_code, mimetype='application/javascript')

@app.route('/robots.txt')
def robots():
    content = f"""User-agent: *
Allow: /
Sitemap: {SITE_URL}/sitemap.xml
"""
    return Response(content, mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap():
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>2026-09-17</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>"""
    return Response(content, mimetype='application/xml')

@app.route('/api/download', methods=['POST'])
def api_download():
    payload = request.get_json() or {}
    url = payload.get('url', '').strip()

    if not url:
        return jsonify({'success': False, 'error': 'Kripya valid video URL dalein.'}), 400

    # yt-dlp configuration with YouTube Android client bypass
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'noplaylist': True,
        'geo_bypass': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title') or 'Social Media Video'
            thumb = info.get('thumbnail') or ''
            direct_video = ''
            server2 = ''
            audio_url = ''

            # Check formats
            formats = info.get('formats', [])
            
            # Find direct video with audio
            for f in formats:
                f_url = f.get('url', '')
                if not f_url:
                    continue
                vcodec = f.get('vcodec', 'none')
                acodec = f.get('acodec', 'none')

                # Combined stream
                if vcodec != 'none' and acodec != 'none':
                    direct_video = f_url
                    server2 = f_url
                # Audio only
                if vcodec == 'none' and acodec != 'none':
                    audio_url = f_url

            # Fallback direct url if combined not found
            if not direct_video:
                direct_video = info.get('url') or (formats[-1].get('url') if formats else '')
            if not server2:
                server2 = direct_video
            if not audio_url:
                audio_url = direct_video

            return jsonify({
                'success': True,
                'title': title,
                'thumbnail': thumb,
                'download_hd': direct_video,
                'download_server2': server2,
                'download_mp3': audio_url
            })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Fetch error: {str(e)[:120]}'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
