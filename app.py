from flask import Flask, render_template_string, request, jsonify
import cloudinary
import cloudinary.uploader
import secrets
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
)

TRACKS_FILE = 'tracks.json'

def load_tracks():
    if os.path.exists(TRACKS_FILE):
        with open(TRACKS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_tracks(tracks):
    with open(TRACKS_FILE, 'w') as f:
        json.dump(tracks, f, indent=2)

def increment_stat(secret_id, stat_type):
    tracks = load_tracks()
    if secret_id in tracks:
        tracks[secret_id][stat_type] = tracks[secret_id].get(stat_type, 0) + 1
        save_tracks(tracks)

@app.route('/')
def home():
    tracks = load_tracks()
    total_plays = sum(track.get('plays', 0) for track in tracks.values())
    total_downloads = sum(track.get('downloads', 0) for track in tracks.values())
    
    html = '''<!DOCTYPE html><html><head><title>Audio Upload</title><meta name="viewport" content="width=device-width, initial-scale=1"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,sans-serif;background:linear-gradient(135deg,#0f0c29 0%,#302b63 50%,#24243e 100%);min-height:100vh;padding:20px;color:#fff}.container{max-width:1000px;margin:0 auto;background:rgba(30,30,40,.95);border-radius:24px;padding:50px;box-shadow:0 25px 80px rgba(0,0,0,.5);border:1px solid rgba(255,255,255,.1)}h1{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:3rem;margin-bottom:10px;text-align:center;font-weight:800}.subtitle{text-align:center;color:#a0a0b0;margin-bottom:50px;font-size:1.1rem}.upload-zone{border:3px dashed rgba(102,126,234,.5);border-radius:20px;padding:50px;text-align:center;background:rgba(102,126,234,.05);margin-bottom:30px}.file-label{display:inline-block;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:18px 50px;border-radius:50px;cursor:pointer;font-weight:700;font-size:1.1rem}input[type=file]{display:none}.form-group{margin-bottom:25px}label{display:block;font-weight:700;color:#e0e0f0;margin-bottom:10px;font-size:.95rem;text-transform:uppercase}input[type=text]{width:100%;padding:16px 20px;border:2px solid rgba(255,255,255,.1);border-radius:12px;font-size:1rem;background:rgba(20,20,30,.6);color:#fff}input[type=text]:focus{outline:0;border-color:#667eea}.upload-btn{width:100%;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:18px;border:none;border-radius:14px;font-size:1.2rem;font-weight:700;cursor:pointer}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-bottom:40px}.stat-card{background:linear-gradient(135deg,rgba(102,126,234,.2) 0%,rgba(118,75,162,.2) 100%);padding:30px;border-radius:18px;text-align:center;border:1px solid rgba(255,255,255,.1)}.stat-number{font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.stat-label{color:#a0a0b0;font-size:.9rem;margin-top:8px;font-weight:600;text-transform:uppercase}.track-item{background:rgba(20,20,30,.6);padding:25px;border-radius:16px;margin-bottom:20px;border-left:5px solid #667eea}.track-title{font-size:1.4rem;font-weight:700;color:#fff;margin-bottom:8px}.track-artist{color:#a0a0b0;margin-bottom:15px}.secret-link{background:rgba(0,0,0,.3);padding:12px;border-radius:10px;border:1px solid rgba(102,126,234,.3);font-family:monospace;word-break:break-all;margin:10px 0;color:#667eea;font-size:.9rem}.copy-btn{background:linear-gradient(135deg,#4caf50 0%,#45a049 100%);color:#fff;border:none;padding:10px 25px;border-radius:8px;cursor:pointer;font-weight:700}</style></head><body><div class="container"><h1>Audio Upload & Share</h1><p class="subtitle">Upload audio files and get secret shareable links</p><div class="stats"><div class="stat-card"><div class="stat-number">''' + str(len(tracks)) + '''</div><div class="stat-label">Tracks</div></div><div class="stat-card"><div class="stat-number">''' + str(total_plays) + '''</div><div class="stat-label">Plays</div></div><div class="stat-card"><div class="stat-number">''' + str(total_downloads) + '''</div><div class="stat-label">Downloads</div></div></div><form id="uploadForm" enctype="multipart/form-data"><div class="upload-zone"><label for="audioFile" class="file-label">Choose Audio File</label><input type="file" id="audioFile" name="audio" accept="audio/*" required><p style="margin-top:15px;color:#8080a0">Max: 100 MB</p></div><div class="form-group"><label>Track Title *</label><input type="text" name="title" required></div><div class="form-group"><label>Artist Name</label><input type="text" name="artist"></div><button type="submit" class="upload-btn">Upload</button></form><div style="margin-top:50px"><h2 style="margin-bottom:25px;color:#fff">My Tracks</h2>'''
    
    if tracks:
        for secret_id, track in tracks.items():
            link = request.url_root + 'listen/' + secret_id
            html += '''<div class="track-item"><div class="track-title">''' + track['title'] + '''</div><div class="track-artist">''' + (track.get('artist') or 'Unknown') + '''</div><div class="secret-link">''' + link + '''</div><button class="copy-btn" onclick="navigator.clipboard.writeText('''' + link + '''')">Copy Link</button></div>'''
    else:
        html += '<p style="text-align:center;color:#8080a0;padding:40px">No tracks yet</p>'
    
    html += '''</div></div><script>document.getElementById("uploadForm").addEventListener("submit",async function(e){e.preventDefault();const t=new FormData(e.target),n=document.querySelector(".upload-btn");n.disabled=!0,n.textContent="Uploading...";try{const e=await fetch("/upload",{method:"POST",body:t}),a=await e.json();a.success?(alert("Upload successful!"),window.location.reload()):alert("Failed: "+a.error)}catch(e){alert("Error: "+e.message)}finally{n.disabled=!1,n.textContent="Upload"}});</script></body></html>'''
    
    return html

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No file'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        title = request.form.get('title', 'Untitled')
        artist = request.form.get('artist', '')
        
        audio_file.seek(0, 2)
        file_size = audio_file.tell()
        audio_file.seek(0)
        
        if file_size > 100 * 1024 * 1024:
            return jsonify({'success': False, 'error': 'File too large'}), 400
        
        result = cloudinary.uploader.upload(audio_file, resource_type="video", folder="audio_tracks")
        
        secret_id = secrets.token_urlsafe(16)
        tracks = load_tracks()
        tracks[secret_id] = {
            'title': title,
            'artist': artist,
            'audio_url': result['secure_url'],
            'cloudinary_id': result['public_id'],
            'uploaded_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'plays': 0,
            'downloads': 0
        }
        save_tracks(tracks)
        
        return jsonify({'success': True, 'secret_id': secret_id}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/listen/<secret_id>')
def listen(secret_id):
    tracks = load_tracks()
    track = tracks.get(secret_id)
    if not track:
        return "Track not found", 404
    
    html = '''<!DOCTYPE html><html><head><title>''' + track['title'] + '''</title><meta name="viewport" content="width=device-width, initial-scale=1"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,sans-serif;background:linear-gradient(135deg,#0f0c29 0%,#302b63 50%,#24243e 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;color:#fff}.player{background:rgba(30,30,40,.95);border-radius:30px;padding:50px;max-width:700px;width:100%;text-align:center;border:1px solid rgba(255,255,255,.1)}.cover{width:320px;height:320px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:24px;margin:0 auto 40px;display:flex;align-items:center;justify-content:center;font-size:8rem}h1{font-size:2.5rem;margin-bottom:15px;font-weight:800}.artist{color:#a0a0b0;font-size:1.3rem;margin-bottom:40px}.waveform{margin:30px 0;padding:20px;background:rgba(0,0,0,.3);border-radius:16px;display:flex;justify-content:center;gap:4px;height:80px;align-items:center}.bar{width:6px;background:linear-gradient(180deg,#667eea 0%,#764ba2 100%);border-radius:3px;animation:wave 1.2s ease-in-out infinite}@keyframes wave{0%,100%{height:20px;opacity:.4}50%{height:80px;opacity:1}}.bar:nth-child(1){animation-delay:0s}.bar:nth-child(2){animation-delay:.1s}.bar:nth-child(3){animation-delay:.2s}.bar:nth-child(4){animation-delay:.3s}.bar:nth-child(5){animation-delay:.4s}.bar:nth-child(6){animation-delay:.5s}.bar:nth-child(7){animation-delay:.6s}.bar:nth-child(8){animation-delay:.5s}.bar:nth-child(9){animation-delay:.4s}.bar:nth-child(10){animation-delay:.3s}.bar:nth-child(11){animation-delay:.2s}.bar:nth-child(12){animation-delay:.1s}audio{width:100%;margin:20px 0}.download-btn{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:18px 50px;border:none;border-radius:50px;font-size:1.1rem;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block}.stats{margin-top:40px;display:flex;justify-content:center;gap:40px;color:#a0a0b0}.stat-item{padding:12px 24px;background:rgba(102,126,234,.1);border-radius:12px}</style></head><body><div class="player"><div class="cover">🎵</div><h1>''' + track['title'] + '''</h1><p class="artist">''' + (track.get('artist') or 'Unknown Artist') + '''</p><div class="waveform"><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div></div><audio controls autoplay id="player"><source src="''' + track['audio_url'] + '''" type="audio/mpeg"></audio><a href="''' + track['audio_url'] + '''" download class="download-btn" onclick="fetch('/api/increment/''' + secret_id + '''/downloads',{method:'POST'})">Download</a><div class="stats"><div class="stat-item">''' + str(track.get('plays', 0)) + ''' plays</div><div class="stat-item">''' + str(track.get('downloads', 0)) + ''' downloads</div></div></div><script>document.getElementById("player").addEventListener("play",function(){fetch("/api/increment/''' + secret_id + '''/plays",{method:"POST"})},{once:!0});</script></body></html>'''
    
    return html

@app.route('/api/increment/<secret_id>/<stat_type>', methods=['POST'])
def increment(secret_id, stat_type):
    if stat_type in ['plays', 'downloads']:
        increment_stat(secret_id, stat_type)
        return jsonify({'success': True})
    return jsonify({'success': False})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
