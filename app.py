from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import cloudinary
import cloudinary.uploader
import cloudinary.api
import secrets
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'your_cloud_name'),
    api_key = os.environ.get('CLOUDINARY_API_KEY', 'your_api_key'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET', 'your_api_secret')
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

HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Audio Upload and Share</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            padding: 20px;
            color: #fff;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(30, 30, 40, 0.95);
            border-radius: 24px;
            padding: 50px;
            box-shadow: 0 25px 80px rgba(0,0,0,0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 3rem;
            margin-bottom: 10px;
            text-align: center;
            font-weight: 800;
            letter-spacing: -1px;
        }
        .subtitle {
            text-align: center;
            color: #a0a0b0;
            margin-bottom: 50px;
            font-size: 1.1rem;
            font-weight: 500;
        }
        .upload-zone {
            border: 3px dashed rgba(102, 126, 234, 0.5);
            border-radius: 20px;
            padding: 50px;
            text-align: center;
            background: rgba(102, 126, 234, 0.05);
            margin-bottom: 30px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .upload-zone::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
            animation: pulse 4s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        .upload-zone:hover {
            border-color: rgba(102, 126, 234, 0.8);
            background: rgba(102, 126, 234, 0.1);
            transform: translateY(-2px);
        }
        .upload-icon {
            font-size: 4rem;
            margin-bottom: 20px;
            position: relative;
            z-index: 1;
        }
        input[type="file"] {
            display: none;
        }
        .file-label {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 18px 50px;
            border-radius: 50px;
            cursor: pointer;
            font-weight: 700;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            position: relative;
            z-index: 1;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        .file-label:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            font-weight: 700;
            color: #e0e0f0;
            margin-bottom: 10px;
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        input[type="text"] {
            width: 100%;
            padding: 16px 20px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            font-size: 1rem;
            background: rgba(20, 20, 30, 0.6);
            color: #fff;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            background: rgba(20, 20, 30, 0.8);
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
        }
        input[type="text"]::placeholder {
            color: rgba(255, 255, 255, 0.3);
        }
        .upload-btn {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 18px;
            border: none;
            border-radius: 14px;
            font-size: 1.2rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        .upload-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
        }
        .upload-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .selected-file {
            margin-top: 20px;
            padding: 12px 20px;
            background: rgba(76, 175, 80, 0.2);
            border-radius: 10px;
            color: #4caf50;
            font-weight: 600;
            display: none;
            border: 1px solid rgba(76, 175, 80, 0.3);
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
            padding: 30px;
            border-radius: 18px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3);
        }
        .stat-number {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .stat-label {
            color: #a0a0b0;
            font-size: 0.9rem;
            margin-top: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .my-tracks {
            margin-top: 50px;
        }
        .track-item {
            background: rgba(20, 20, 30, 0.6);
            padding: 25px;
            border-radius: 16px;
            margin-bottom: 20px;
            border-left: 5px solid #667eea;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .track-item:hover {
            background: rgba(20, 20, 30, 0.8);
            transform: translateX(5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        .track-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #fff;
            margin-bottom: 8px;
        }
        .track-artist {
            color: #a0a0b0;
            margin-bottom: 15px;
            font-weight: 500;
        }
        .track-stats {
            display: flex;
            gap: 25px;
            font-size: 0.9rem;
            color: #8080a0;
            margin-bottom: 15px;
            font-weight: 600;
        }
        .secret-link {
            background: rgba(0, 0, 0, 0.3);
            padding: 12px 15px;
            border-radius: 10px;
            border: 1px solid rgba(102, 126, 234, 0.3);
            font-family: 'Courier New', monospace;
            word-break: break-all;
            margin-bottom: 12px;
            color: #667eea;
            font-size: 0.9rem;
        }
        .copy-btn {
            background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
            color: white;
            border: none;
            padding: 10px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 700;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .copy-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(76, 175, 80, 0.4);
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Audio Upload & Share</h1>
        <p class="subtitle">Upload audio files and get secret shareable links</p>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ total_tracks }}</div>
                <div class="stat-label">Total Tracks</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_plays }}</div>
                <div class="stat-label">Total Plays</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_downloads }}</div>
                <div class="stat-label">Total Downloads</div>
            </div>
        </div>

        <form id="uploadForm" enctype="multipart/form-data">
            <div class="upload-zone">
                <div class="upload-icon">🎧</div>
                <label for="audioFile" class="file-label">Choose Audio File</label>
                <input type="file" id="audioFile" name="audio" accept="audio/*" required>
                <div id="selectedFile" class="selected-file"></div>
                <p style="margin-top: 15px; color: #8080a0; font-size: 0.9rem;">
                    Max file size: 100 MB
                </p>
            </div>

            <div class="form-group">
                <label>Track Title *</label>
                <input type="text" name="title" placeholder="Enter track title" required>
            </div>

            <div class="form-group">
                <label>Artist Name</label>
                <input type="text" name="artist" placeholder="Enter artist name (optional)">
            </div>

            <button type="submit" class="upload-btn" id="uploadBtn">
                Upload & Generate Secret Link
            </button>
        </form>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 15px; color: #667eea; font-weight: bold;">Uploading...</p>
        </div>

        <div class="my-tracks">
            <h2 style="margin-bottom: 25px; color: #fff; font-weight: 700; font-size: 1.8rem;">My Uploaded Tracks</h2>
            {% if tracks %}
                {% for secret_id, track in tracks.items() %}
                <div class="track-item">
                    <div class="track-title">{{ track.title }}</div>
                    <div class="track-artist">{{ track.artist or 'Unknown Artist' }}</div>
                    <div class="track-stats">
                        <span>{{ track.plays or 0 }} plays</span>
                        <span>{{ track.downloads or 0 }} downloads</span>
                        <span>{{ track.uploaded_at }}</span>
                    </div>
                    <div class="secret-link">{{ request.url_root }}listen/{{ secret_id }}</div>
                    <button class="copy-btn" onclick="copyLink('{{ request.url_root }}listen/{{ secret_id }}')">
                        Copy Link
                    </button>
                </div>
                {% endfor %}
            {% else %}
                <p style="text-align: center; color: #8080a0; padding: 40px;">No tracks uploaded yet.</p>
            {% endif %}
        </div>
    </div>

    <script>
        document.getElementById('audioFile').addEventListener('change', function(e) {
            const file = e.target.files[0];
            const selectedFile = document.getElementById('selectedFile');
            
            if (file) {
                const fileSizeMB = file.size / (1024 * 1024);
                
                if (fileSizeMB > 100) {
                    alert('File too large! Maximum is 100 MB. Your file: ' + fileSizeMB.toFixed(2) + ' MB');
                    e.target.value = '';
                    selectedFile.style.display = 'none';
                    return;
                }
                
                selectedFile.innerHTML = 'Selected: ' + file.name + ' (' + fileSizeMB.toFixed(2) + ' MB)';
                selectedFile.style.display = 'block';
            }
        });

        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const uploadBtn = document.getElementById('uploadBtn');
            const loading = document.getElementById('loading');
            
            uploadBtn.disabled = true;
            loading.style.display = 'block';
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Upload successful! Your secret link has been generated.');
                    window.location.reload();
                } else {
                    alert('Upload failed: ' + result.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                uploadBtn.disabled = false;
                loading.style.display = 'none';
            }
        });

        function copyLink(link) {
            navigator.clipboard.writeText(link).then(function() {
                alert('Link copied!');
            });
        }
    </script>
</body>
</html>
"""

LISTEN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ track.title }} - Listen</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            color: #fff;
        }
        .player-container {
            background: rgba(30, 30, 40, 0.95);
            border-radius: 30px;
            padding: 50px;
            max-width: 700px;
            width: 100%;
            box-shadow: 0 30px 100px rgba(0,0,0,0.6);
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        .cover {
            width: 320px;
            height: 320px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 24px;
            margin: 0 auto 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 8rem;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.5);
            position: relative;
            overflow: hidden;
        }
        .cover::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.2) 0%, transparent 60%);
        }
        h1 {
            font-size: 2.5rem;
            color: #fff;
            margin-bottom: 15px;
            font-weight: 800;
            letter-spacing: -1px;
        }
        .artist {
            color: #a0a0b0;
            font-size: 1.3rem;
            margin-bottom: 40px;
            font-weight: 600;
        }
        .waveform-container {
            margin: 30px 0;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 16px;
            border: 1px solid rgba(102, 126, 234, 0.3);
        }
        .waveform {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            height: 80px;
        }
        .bar {
            width: 6px;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            border-radius: 3px;
            animation: wave 1.2s ease-in-out infinite;
            opacity: 0.7;
        }
        .bar:nth-child(1) { animation-delay: 0s; }
        .bar:nth-child(2) { animation-delay: 0.1s; }
        .bar:nth-child(3) { animation-delay: 0.2s; }
        .bar:nth-child(4) { animation-delay: 0.3s; }
        .bar:nth-child(5) { animation-delay: 0.4s; }
        .bar:nth-child(6) { animation-delay: 0.5s; }
        .bar:nth-child(7) { animation-delay: 0.6s; }
        .bar:nth-child(8) { animation-delay: 0.5s; }
        .bar:nth-child(9) { animation-delay: 0.4s; }
        .bar:nth-child(10) { animation-delay: 0.3s; }
        .bar:nth-child(11) { animation-delay: 0.2s; }
        .bar:nth-child(12) { animation-delay: 0.1s; }
        @keyframes wave {
            0%, 100% { height: 20px; opacity: 0.4; }
            50% { height: 80px; opacity: 1; }
        }
        .waveform.paused .bar {
            animation-play-state: paused;
            height: 20px;
            opacity: 0.4;
        }
        audio {
            width: 100%;
            margin-bottom: 30px;
            border-radius: 12px;
            filter: contrast(1.2) brightness(1.1);
        }
        audio::-webkit-media-controls-panel {
            background: rgba(102, 126, 234, 0.2);
        }
        .download-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 18px 50px;
            border: none;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        .download-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
        }
        .stats {
            margin-top: 40px;
            display: flex;
            justify-content: center;
            gap: 40px;
            color: #a0a0b0;
            font-weight: 600;
        }
        .stat-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 24px;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 12px;
            border: 1px solid rgba(102, 126, 234, 0.2);
        }
    </style>
</head>
<body>
    <div class="player-container">
        <div class="cover">🎵</div>
        <h1>{{ track.title }}</h1>
        <p class="artist">{{ track.artist or 'Unknown Artist' }}</p>
        
        <div class="waveform-container">
            <div class="waveform" id="waveform">
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
            </div>
        </div>
        
        <audio controls autoplay id="audioPlayer">
            <source src="{{ track.audio_url }}" type="audio/mpeg">
        </audio>
        
        <a href="{{ track.audio_url }}" download class="download-btn" onclick="incrementDownload()">
            Download Track
        </a>
        
        <div class="stats">
            <div class="stat-item">
                <span>▶️</span>
                <span>{{ track.plays or 0 }} plays</span>
            </div>
            <div class="stat-item">
                <span>⬇️</span>
                <span>{{ track.downloads or 0 }} downloads</span>
            </div>
        </div>
    </div>

    <script>
        const audioPlayer = document.getElementById('audioPlayer');
        const waveform = document.getElementById('waveform');
        
        audioPlayer.addEventListener('play', function() {
            waveform.classList.remove('paused');
            fetch('/api/increment/{{ secret_id }}/plays', { method: 'POST' });
        }, { once: true });
        
        audioPlayer.addEventListener('pause', function() {
            waveform.classList.add('paused');
        });
        
        audioPlayer.addEventListener('ended', function() {
            waveform.classList.add('paused');
        });

        function incrementDownload() {
            fetch('/api/increment/{{ secret_id }}/downloads', { method: 'POST' });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    tracks = load_tracks()
    total_plays = sum(track.get('plays', 0) for track in tracks.values())
    total_downloads = sum(track.get('downloads', 0) for track in tracks.values())
    
    return render_template_string(HOME_TEMPLATE, 
                                 tracks=tracks, 
                                 total_tracks=len(tracks),
                                 total_plays=total_plays,
                                 total_downloads=total_downloads)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'})
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        title = request.form.get('title', 'Untitled')
        artist = request.form.get('artist', '')
        
        audio_file.seek(0, 2)
        file_size = audio_file.tell()
        audio_file.seek(0)
        
        if file_size > 100 * 1024 * 1024:
            return jsonify({'success': False, 'error': 'File too large. Maximum size is 100 MB.'})
        
        if not cloudinary.config().cloud_name or cloudinary.config().cloud_name == 'your_cloud_name':
            return jsonify({'success': False, 'error': 'Cloudinary not configured.'})
        
        result = cloudinary.uploader.upload(
            audio_file,
            resource_type="video",
            folder="audio_tracks",
            chunk_size=6000000
        )
        
        secret_id = secrets.token_urlsafe(16)
        
        tracks = load_tracks()
        tracks[secret_id] = {
            'title': title,
            'artist': artist,
            'audio_url': result['secure_url'],
            'cloudinary_id': result['public_id'],
            'uploaded_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'plays': 0,
            'downloads': 0,
            'file_size_mb': round(file_size / (1024 * 1024), 2)
        }
        save_tracks(tracks)
        
        return jsonify({'success': True, 'secret_id': secret_id})
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/listen/<secret_id>')
def listen(secret_id):
    tracks = load_tracks()
    track = tracks.get(secret_id)
    
    if not track:
        return "Track not found", 404
    
    return render_template_string(LISTEN_TEMPLATE, track=track, secret_id=secret_id)

@app.route('/api/increment/<secret_id>/<stat_type>', methods=['POST'])
def increment(secret_id, stat_type):
    if stat_type in ['plays', 'downloads']:
        increment_stat(secret_id, stat_type)
        return jsonify({'success': True})
    return jsonify({'success': False})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
