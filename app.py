from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests
import re

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

def fetch_youtube_clean(url):
    """Bypasses YouTube datacenter ban using rapid multi-instance resolvers"""
    instances = [
        "https://api.cobalt.tools",
        "https://cobalt.api.scav.info",
        "https://co.eik.top"
    ]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    payload = {
        "url": url,
        "videoQuality": "720",
        "audioFormat": "mp3",
        "downloadMode": "auto"
    }

    for inst in instances:
        try:
            r = requests.post(f"{inst}", json=payload, headers=headers, timeout=6)
            if r.status_code == 200:
                data = r.json()
                dl_url = data.get("url")
                if dl_url:
                    return {
                        'success': True,
                        'title': 'YouTube Video (HD)',
                        'thumbnail': 'https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=400',
                        'download_hd': dl_url,
                        'download_server2': dl_url,
                        'download_mp3': dl_url
                    }
        except Exception:
            continue
    return None

@app.route('/api/download', methods=['POST'])
def api_download():
    payload = request.get_json() or {}
    url = payload.get('url', '').strip()

    if not url:
        return jsonify({'success': False, 'error': 'Kripya video URL enter karein.'}), 400

    is_yt = bool(re.search(r'(youtube\.com|youtu\.be)', url, re.IGNORECASE))

    # If YouTube, directly route to bypass resolvers
    if is_yt:
        res = fetch_youtube_clean(url)
        if res:
            return jsonify(res)

    # Standard engine for Instagram, TikTok, Facebook, Twitter, Reddit
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'noplaylist': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title') or 'Social Media Video'
            thumb = info.get('thumbnail') or ''
            direct_video = ''
            audio_url = ''

            formats = info.get('formats', [])
            for f in formats:
                f_url = f.get('url', '')
                if not f_url:
                    continue
                vcodec = f.get('vcodec', 'none')
                acodec = f.get('acodec', 'none')

                if vcodec != 'none' and acodec != 'none':
                    direct_video = f_url
                if vcodec == 'none' and acodec != 'none':
                    audio_url = f_url

            if not direct_video and formats:
                direct_video = formats[-1].get('url', '')
            if not audio_url:
                audio_url = direct_video

            return jsonify({
                'success': True,
                'title': title,
                'thumbnail': thumb,
                'download_hd': direct_video,
                'download_server2': direct_video,
                'download_mp3': audio_url
            })

    except Exception as e:
        return jsonify({'success': False, 'error': 'Video stream extract nahi ho paya. URL check karein.'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
