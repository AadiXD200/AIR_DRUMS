"""
Flask web application for Air Drums
"""

from flask import Flask, render_template, send_from_directory, jsonify
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'air-drums-secret-key'

# Get base path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, 'audio')


@app.route('/')
def landing():
    """Landing page"""
    return render_template('landing.html')


@app.route('/play')
def play():
    """Main drum kit interface"""
    return render_template('play.html')


@app.route('/audio/<drum_type>/<filename>')
def serve_audio(drum_type, filename):
    """Serve audio files"""
    # Handle case variations - try different folder name combinations
    possible_folders = [
        drum_type.lower(),
        drum_type.capitalize(),
        drum_type.upper(),
        drum_type,
    ]
    
    # Handle "hat" -> "Hat" special case
    if drum_type.lower() == 'hat':
        possible_folders.insert(0, 'Hat')
    
    for folder in possible_folders:
        folder_path = os.path.join(AUDIO_DIR, folder)
        file_path = os.path.join(folder_path, filename)
        
        if os.path.exists(file_path):
            return send_from_directory(folder_path, filename)
    
    return "Audio file not found", 404


@app.route('/api/audio-list')
def audio_list():
    """Get list of available audio files"""
    audio_files = {}
    drum_types = ['kick', 'snare', 'tom', 'floor', 'hat', 'ride']
    
    for drum_type in drum_types:
        audio_files[drum_type] = []
        # Try different case variations
        possible_dirs = [
            os.path.join(AUDIO_DIR, drum_type),
            os.path.join(AUDIO_DIR, drum_type.lower()),
            os.path.join(AUDIO_DIR, drum_type.capitalize()),
        ]
        
        for dir_path in possible_dirs:
            if os.path.exists(dir_path):
                files = [f for f in os.listdir(dir_path) if f.endswith('.wav')]
                files.sort()
                audio_files[drum_type] = [f'/audio/{drum_type}/{f}' for f in files]
                break
    
    return jsonify(audio_files)


if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    # Get port from environment variable (Cloud Run provides PORT=8080)
    # Default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    
    print("="*60)
    print("Air Drums Web Application")
    print("="*60)
    print(f"Starting server at http://0.0.0.0:{port}")
    print(f"Audio directory: {AUDIO_DIR}")
    print(f"Debug mode: {debug_mode}")
    print("="*60)
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

