from flask import Flask, render_template_string, request, redirect, url_for, jsonify, send_file
import cloudinary
import cloudinary.uploader
import cloudinary.api
import secrets
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configure Cloudinary
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'your_cloud_name'),
    api_key = os.environ.get('CLOUDINARY_API_KEY', 'your_api_key'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET', 'your_api_secret')
)

# Simple file-based database
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

# HTML Templates
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Audio Upload & Share</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 40px;
        }
        .upload-zone {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            background: #f8f9ff;
            margin-bottom: 30px;
            transition: all 0.3s;
        }
        .upload-zone:hover {
            border-color: #764ba2;
            background: #f0f2ff;
        }
        .upload-icon {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        input[type="file"] {
            display: none;
        }
        .file-label {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border-radius: 30px;
            cursor: pointer;
            font-weight: bold;
            font-size: 1.1rem;
            transition: transform 0.2s;
        }
        .file-label:hover {
            transform: scale(1.05);
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        .upload-btn {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 1.2rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .upload-btn:hover {
            transform: translateY(-2px);
        }
        .upload-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .selected-file {
            margin-top: 15px;
            padding: 10px;
            background: #e8f5e9;
            border-radius: 8px;
            color: #2e7d32;
            font-weight: bold;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            font-size: 0.9rem;
            margin-top: 5px;
        }
        .my-tracks {
            margin-top: 40px;
        }
        .track-item {
            background: #f8f9ff;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        .track-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .track-artist {
            color: #666;
            margin-bottom: 10px;
        }
        .track-stats {
            display: flex;
            gap: 20px;
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 10px;
        }
        .secret-link {
            background: #fff;
            padding: 10px;
            border-radius: 8px;
            border: 2px solid #667eea;
            font-family: monospace;
            word-break: break-all;
            margin-bottom: 10px;
        }
        .copy-btn {
            background: #4caf50;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        }
        .copy-btn:hover {
            background: #45a049;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
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
        <h1>🎵 Audio Upload & Share</h1>
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
                <div id="selectedFile" class="selected-file" style="display:none;"></div>
                <p style="margin-top: 15px; color: #999; font-size: 0.9rem;">
                    Max file size: 100 MB • Supported: MP3, WAV, M4A, etc.
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
                📤 Upload & Generate Secret Link
            </button>
        </form>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 15px; color: #667eea; font-weight: bold;">Uploading to Cloudinary...</p>
        </div>

        <div class="my-tracks">
            <h2 style="margin-bottom: 20px; color: #333;">📚 My Uploaded Tracks</h2>
            {% if tracks %}
                {% for secret_id, track in tracks.items() %}
                <div class="track-item">
                    <div class="track-title">{{ track.title }}</div>
                    <div class="track-artist">{{ track.artist or 'Unknown Artist' }}</div>
                    <div class="track-stats">
                        <span>▶️ {{ track.plays or 0 }} plays</span>
                        <span>⬇️ {{ track.downloads or 0 }} downloads</span>
                        <span>📅 {{ track.uploaded_at }}</span>
                    </div>
                    <div class="secret-link">{{ request.url_root }}listen/{{ secret_id }}</div>
                    <button class="copy-btn" onclick="copyLink('{{ request.url_root }}listen/{{ secret_id }}')">
                        📋 Copy Link
                    </button>
                </div>
                {% endfor %}
            {% else %}
                <p style="text-align: center; color: #999; padding: 40px;">No tracks uploaded yet. Upload your first track above! 🎵</p>
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
                    alert('❌ File too large! Maximum file size is 100 MB.\\nYour file: ' + fileSizeMB.toFixed(2) + ' MB');
                    e.target.value = '';
                    selectedFile.style.display = 'none';
                    return;
                }
                
                selectedFile.innerHTML = '✓ Selected: ' + file.name + ' (' + fileSizeMB.toFixed(2) + ' MB)';
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
                    alert('✅ Upload successful! Your secret link has been generated.');
                    window.location.reload();
                } else {
                    alert('❌ Upload failed: ' + result.error);
                }
            } catch (error) {
                alert('❌ Error: ' + error.message);
            } finally {
                uploadBtn.disabled = false;
                loading.style.display = 'none';
            }
        });

        function copyLink(link) {
            navigator.clipboard.writeText(link).then(() => {
                alert('✅ Link copied to clipboard!');
            });
        }
    </script>
</body>
</html>
'''

LISTEN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ track.title }} - Listen</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .player-container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }
        .cover {
            width: 300px;
            height: 300px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            margin: 0 auto 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 6rem;
        }
        h1 {
            font-size: 2rem;
            color: #333;
            margin-bottom: 10px;
        }
        .artist {
            color: #666;
            font-size: 1.2rem;
            margin-bottom: 30px;
        }
        audio {
            width: 100%;
            margin-bottom: 20px;
            border-radius: 10px;
        }
        .download-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 30px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: transform 0.2s;
        }
        .download-btn:hover {
            transform: scale(1.05);
        }
        .stats {
            margin-top: 30px;
            display: flex;
            justify-content: center;
            gap: 30px;
            color: #666;
        }
        .stat-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
    </style>
</head>
<body>
    <div class="player-container">
        <div class="cover">🎵</div>
        <h1>{{ track.title }}</h1>
        <p class="artist">{{ track.artist or 'Unknown Artist' }}</p>
        
        <audio controls autoplay id="audioPlayer">
            <source src="{{ track.audio_url }}" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
        
        <a href="{{ track.audio_url }}" download class="download-btn" onclick="incrementDownload()">
            ⬇️ Download Track
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
        document.getElementById('audioPlayer').addEventListener('play', function() {
            fetch('/api/increment/{{ secret_id }}/plays', { method: 'POST' });
        }, { once: true });

        function incrementDownload() {
            fetch('/api/increment/{{ secret_id }}/downloads', { method: 'POST' });
        }
    </script>
</body>
</html>
'''

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
        audio_file = request.files['audio']
        title = request.form.get('title', 'Untitled')
        artist = request.form.get('artist', '')
        
        # Check file size (100 MB limit for Cloudinary free plan)
        audio_file.seek(0, 2)  # Seek to end
        file_size = audio_file.tell()  # Get file size
        audio_file.seek(0)  # Reset to beginning
        
        if file_size > 100 * 1024 * 1024:  # 100 MB in bytes
            return jsonify({'success': False, 'error': 'File too large. Maximum size is 100 MB.'})
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            audio_file,
            resource_type="video",  # Cloudinary uses 'video' for audio files
            folder="audio_tracks",
            chunk_size=6000000  # 6MB chunks for large files
        )
        
        # Generate secret ID
        secret_id = secrets.token_urlsafe(16)
        
        # Save track info
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
