# backend/config.py
import os

class Config:
    SECRET_KEY = 'dyslexia-assistant-secret-key'
    DEBUG = True
    
    # Use absolute paths to avoid issues with relative paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    SELECTIONS_FOLDER = os.path.join(BASE_DIR, 'static', 'selections')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SPEECH_RATE = 100
    SIMILARITY_THRESHOLD = 0.75

# Create directories without any fancy error handling
try:
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)
    if not os.path.exists(Config.SELECTIONS_FOLDER):
        os.makedirs(Config.SELECTIONS_FOLDER)
    print("Directories are ready")
except:
    print("Directories already exist - continuing")