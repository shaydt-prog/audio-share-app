from flask import Flask, request, jsonify
import cloudinary
import cloudinary.uploader
import secrets
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['JSON_AS_ASCII'] = False

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
    
    html = '<!DOCTYPE html><html><head><title>Audio Upload</title><meta name="viewport" content="width=device-width,initial-scale=1"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,sans-serif;background:#000;min-height:100vh;padding:20px;color:#fff}::-webkit-scrollbar{width:8px;background:#000}::-webkit-scrollbar-thumb{background:#333;border-radius:4px}.container{max-width:1000px;margin:0 auto;background:#0a0a0a;border-radius:16px;padding:40px;border:1px solid #1a1a1a}h1{background:linear-gradient(135deg,#fe2c55 0%,#ff6b6b 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:2.8rem;margin-bottom:10px;text-align:center;font-weight:900;letter-spacing:-2px}.subtitle{text-align:center;color:#666;margin-bottom:40px;font-size:1rem;font-weight:500}.upload-zone{border:2px dashed #1a1a1a;border-radius:12px;padding:40px;text-align:center;background:#0f0f0f;margin-bottom:25px;transition:all .3s}.upload-zone:hover{border-color:#fe2c55;background:#111}.file-label{display:inline-block;background:linear-gradient(135deg,#fe2c55 0%,#ff6b6b 100%);color:#fff;padding:14px 40px;border-radius:50px;cursor:pointer;font-weight:800;font-size:1rem;box-shadow:0 4px 20px rgba(254,44,85,.4);transition:transform .2s}.file-label:hover{transform:scale(1.05)}input[type=file]{display:none}.selected-file{margin-top:20px;padding:15px;background:#111;border-radius:8px;color:#fe2c55;font-weight:700;display:none;border:1px solid #1a1a1a}.progress-container{margin-top:20px;display:none}.progress-bar{width:100%;height:4px;background:#1a1a1a;border-radius:2px;overflow:hidden}.progress-fill{height:100%;background:linear-gradient(90deg,#fe2c55 0%,#ff6b6b 100%);width:0;transition:width .3s}.progress-text{margin-top:10px;color:#666;font-size:.9rem;text-align:center}.form-group{margin-bottom:20px}label{display:block;font-weight:700;color:#999;margin-bottom:8px;font-size:.85rem;text-transform:uppercase;letter-spacing:1px}input[type=text]{width:100%;padding:14px 18px;border:1px solid #1a1a1a;border-radius:10px;font-size:1rem;background:#0f0f0f;color:#fff;transition:border .3s}input[type=text]:focus{outline:0;border-color:#fe2c55;background:#111}input[type=text]::placeholder{color:#333}.upload-btn{width:100%;background:linear-gradient(135deg,#fe2c55 0%,#ff6b6b 100%);color:#fff;padding:16px;border:none;border-radius:10px;font-size:1.1rem;font-weight:800;cursor:pointer;transition:transform .2s;box-shadow:0 4px 20px rgba(254,44,85,.4)}.upload-btn:hover{transform:translateY(-2px)}.upload-btn:disabled{opacity:.5;cursor:not-allowed;transform:none}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-bottom:35px}.stat-card{background:#0f0f0f;padding:25px;border-radius:12px;text-align:center;border:1px solid #1a1a1a;transition:all .3s}.stat-card:hover{transform:translateY(-3px);border-color:#fe2c55}.stat-number{font-size:2.2rem;font-weight:900;background:linear-gradient(135deg,#fe2c55 0%,#ff6b6b 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.stat-label{color:#666;font-size:.8rem;margin-top:5px;font-weight:700;text-transform:uppercase;letter-spacing:1px}.track-item{background:#0f0f0f;padding:20px;border-radius:12px;margin-bottom:15px;border-left:4px solid #fe2c55;border:1px solid #1a1a1a;transition:all .3s}.track-item:hover{background:#111;border-color:#fe2c55}.track-title{font-size:1.2rem;font-weight:800;color:#fff;margin-bottom:6px}.track-artist{color:#666;margin-bottom:12px;font-weight:600;font-size:.9rem}.secret-link{background:#000;padding:10px 12px;border-radius:8px;border:1px solid #1a1a1a;font-family:monospace;word-break:break-all;margin:10px 0;color:#fe2c55;font-size:.85rem}.copy-btn{background:#0f0f0f;color:#fe2c55;border:1px solid #1a1a1a;padding:8px 20px;border-radius:6px;cursor:pointer;font-weight:700;font-size:.9rem;transition:all .2s}.copy-btn:hover{background:#fe2c55;color:#fff;border-color:#fe2c55}</style></head><body><div class="container"><h1>AUDIO UPLOAD</h1><p class="subtitle">Upload & share audio with secret links</p><div class="stats"><div class="stat-card"><div class="stat-number">' + str(len(tracks)) + '</div><div class="stat-label">Tracks</div></div><div class="stat-card"><div class="stat-number">' + str(total_plays) + '</div><div class="stat-label">Plays</div></div><div class="stat-card"><div class="stat-number">' + str(total_downloads) + '</div><div class="stat-label">Downloads</div></div></div><form id="uploadForm" enctype="multipart/form-data"><div class="upload-zone"><label for="audioFile" class="file-label">CHOOSE FILE</label><input type="file" id="audioFile" name="audio" accept="audio/*" required><div id="selectedFile" class="selected-file"></div><div class="progress-container" id="progressContainer"><div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div><div class="progress-text" id="progressText">Uploading...</div></div></div><div class="form-group"><label>Track Title</label><input type="text" name="title" placeholder="Enter title" required></div><div class="form-group"><label>Artist Name</label><input type="text" name="artist" placeholder="Enter artist (optional)"></div><button type="submit" class="upload-btn" id="uploadBtn">UPLOAD</button></form><div style="margin-top:45px"><h2 style="margin-bottom:20px;color:#fff;font-weight:900;font-size:1.5rem">MY TRACKS</h2>'
    
    if tracks:
        for secret_id, track in tracks.items():
            link = request.url_root + 'listen/' + secret_id
            html += '<div class="track-item"><div class="track-title">' + track['title'] + '</div><div class="track-artist">' + (track.get('artist') or 'Unknown') + '</div><div class="secret-link">' + link + '</div><button class="copy-btn" onclick="navigator.clipboard.writeText(\'' + link + '\');this.textContent=\'COPIED!\';setTimeout(()=>this.textContent=\'COPY LINK\',2000)">COPY LINK</button></div>'
    else:
        html += '<p style="text-align:center;color:#333;padding:40px">No tracks yet</p>'
    
    html += '</div></div><script>const fileInput=document.getElementById("audioFile"),selectedFile=document.getElementById("selectedFile"),progressContainer=document.getElementById("progressContainer"),progressFill=document.getElementById("progressFill"),progressText=document.getElementById("progressText");fileInput.addEventListener("change",function(e){const file=e.target.files[0];if(file){const sizeMB=(file.size/(1024*1024)).toFixed(2);sizeMB>100?(alert("File too large! Max 100 MB. Your file: "+sizeMB+" MB"),e.target.value="",selectedFile.style.display="none"):(selectedFile.innerHTML="✓ "+file.name+" ("+sizeMB+" MB)",selectedFile.style.display="block")}});document.getElementById("uploadForm").addEventListener("submit",async function(e){e.preventDefault();const form=new FormData(e.target),btn=document.getElementById("uploadBtn"),xhr=new XMLHttpRequest;btn.disabled=!0,btn.textContent="UPLOADING...",progressContainer.style.display="block",progressFill.style.width="0%",xhr.upload.addEventListener("progress",function(e){if(e.lengthComputable){const percent=Math.round(e.loaded/e.total*100);progressFill.style.width=percent+"%",progressText.textContent="Uploading... "+percent+"%"}}),xhr.addEventListener("load",function(){if(200===xhr.status){try{const result=JSON.parse(xhr.responseText);result.success?(alert("Upload successful!"),window.location.reload()):alert("Failed: "+(result.error||"Unknown error"))}catch(e){alert("Error parsing response")}btn.disabled=!1,btn.textContent="UPLOAD",progressContainer.style.display="none"}else alert("Upload failed"),btn.disabled=!1,btn.textContent="UPLOAD",progressContainer.style.display="none"}),xhr.addEventListener("error",function(){alert("Upload error"),btn.disabled=!1,btn.textContent="UPLOAD",progressContainer.style.display="none"}),xhr.open("POST","/upload",!0),xhr.send(form)});</script></body></html>'
    
    return html

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'audio' not in request.files:
            response = jsonify({'success': False, 'error': 'No file'})
            response.status_code = 400
            return response
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            response = jsonify({'success': False, 'error': 'No file selected'})
            response.status_code = 400
            return response
        
        title = request.form.get('title', 'Untitled')
        artist = request.form.get('artist', '')
        
        audio_file.seek(0, 2)
        file_size = audio_file.tell()
        audio_file.seek(0)
        
        if file_size > 100 * 1024 * 1024:
            response = jsonify({'success': False, 'error': 'File too large'})
            response.status_code = 400
            return response
        
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
        
        response = jsonify({'success': True, 'secret_id': secret_id})
        response.status_code = 200
        return response
    except Exception as e:
        app.logger.error('Upload error: ' + str(e))
        response = jsonify({'success': False, 'error': str(e)})
        response.status_code = 500
        return response

@app.route('/listen/<secret_id>')
def listen(secret_id):
    tracks = load_tracks()
    track = tracks.get(secret_id)
    if not track:
        return "Track not found", 404
    
    html = '<!DOCTYPE html><html><head><title>' + track['title'] + '</title><meta name="viewport" content="width=device-width,initial-scale=1"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,sans-serif;background:#000;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;color:#fff}.player{background:#0a0a0a;border-radius:20px;padding:40px;max-width:900px;width:100%;border:1px solid #1a1a1a}.cover{width:200px;height:200px;background:linear-gradient(135deg,#fe2c55 0%,#ff6b6b 100%);border-radius:12px;margin:0 auto 25px;display:flex;align-items:center;justify-content:center;font-size:5rem;box-shadow:0 15px 40px rgba(254,44,85,.3)}h1{font-size:2rem;margin-bottom:8px;font-weight:900;letter-spacing:-1px}.artist{color:#666;font-size:1.1rem;margin-bottom:30px;font-weight:700}.waveform-player{position:relative;margin:30px 0;padding:30px;background:#0f0f0f;border-radius:12px;border:1px solid #1a1a1a}.play-overlay{position:absolute;top:50%;left:40px;transform:translateY(-50%);z-index:10}.play-btn{width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,#fe2c55 0%,#ff6b6b 100%);border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 8px 25px rgba(254,44,85,.5);transition:all .2s}.play-btn:hover{transform:scale(1.1);box-shadow:0 12px 35px rgba(254,44,85,.7)}.play-btn svg{width:24px;height:24px;fill:#fff;margin-left:3px}.play-btn.playing svg{margin-left:0}#waveform{cursor:pointer;min-height:120px}.time-display{display:flex;justify-content:space-between;margin-top:15px;font-size:.85rem;color:#666;font-weight:700}.download-btn{background:linear-gradient(135deg,#fe2c55 0%,#ff6b6b 100%);color:#fff;padding:16px 45px;border:none;border-radius:50px;font-size:1rem;font-weight:800;cursor:pointer;transition:transform .2s;box-shadow:0 8px 25px rgba(254,44,85,.4);text-transform:uppercase;letter-spacing:1px;width:100%;margin-top:20px}.download-btn:hover{transform:translateY(-3px);box-shadow:0 12px 35px rgba(254,44,85,.6)}.stats{margin-top:30px;display:flex;justify-content:center;gap:25px;color:#666;font-weight:700}.stat-item{padding:10px 20px;background:#0f0f0f;border-radius:8px;border:1px solid #1a1a1a;font-size:.85rem}</style></head><body><div class="player"><div class="cover">🎵</div><h1>' + track['title'] + '</h1><p class="artist">' + (track.get('artist') or 'Unknown Artist') + '</p><div class="waveform-player"><div class="play-overlay"><button class="play-btn" id="playBtn"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button></div><div id="waveform"></div><div class="time-display"><span id="currentTime">0:00</span><span id="duration">0:00</span></div></div><button class="download-btn" onclick="downloadTrack()">Download Track</button><div class="stats"><div class="stat-item">' + str(track.get('plays', 0)) + ' plays</div><div class="stat-item">' + str(track.get('downloads', 0)) + ' downloads</div></div></div><script src="https://cdn.jsdelivr.net/npm/wavesurfer.js@7.7.15/dist/wavesurfer.min.js"></script><script>let wavesurfer,hasPlayed=!1;const playBtn=document.getElementById("playBtn"),playIcon=\'<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>\',pauseIcon=\'<svg viewBox="0 0 24 24"><path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/></svg>\';function formatTime(e){const t=Math.floor(e/60),a=Math.floor(e%60);return t+":"+(a<10?"0":"")+a}setTimeout(function(){if("undefined"==typeof WaveSurfer)return void console.error("WaveSurfer failed to load");wavesurfer=WaveSurfer.create({container:"#waveform",waveColor:"#1a1a1a",progressColor:"#fe2c55",cursorColor:"#ff6b6b",barWidth:3,barRadius:3,cursorWidth:2,height:120,barGap:2,responsive:!0,normalize:!0}),wavesurfer.load("' + track['audio_url'] + '"),wavesurfer.on("ready",function(){document.getElementById("duration").textContent=formatTime(wavesurfer.getDuration())}),wavesurfer.on("audioprocess",function(){document.getElementById("currentTime").textContent=formatTime(wavesurfer.getCurrentTime())}),wavesurfer.on("play",function(){playBtn.classList.add("playing"),playBtn.innerHTML=pauseIcon,hasPlayed||(fetch("/api/increment/' + secret_id + '/plays",{method:"POST"}),hasPlayed=!0)}),wavesurfer.on("pause",function(){playBtn.classList.remove("playing"),playBtn.innerHTML=playIcon}),playBtn.addEventListener("click",function(){wavesurfer.playPause()}),document.getElementById("waveform").addEventListener("click",function(e){const t=e.offsetX/this.offsetWidth;wavesurfer.seekTo(t)})},100);function downloadTrack(){fetch("/api/increment/' + secret_id + '/downloads",{method:"POST"}),fetch("' + track['audio_url'] + '").then(e=>e.blob()).then(e=>{const t=document.createElement("a"),a=URL.createObjectURL(e);t.href=a,t.download="' + track['title'].replace("'", "").replace('"', '') + '.mp3",document.body.appendChild(t),t.click(),document.body.removeChild(t),URL.revokeObjectURL(a)}).catch(()=>{window.open("' + track['audio_url'] + '","_blank")})}</script></body></html>'
    
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
