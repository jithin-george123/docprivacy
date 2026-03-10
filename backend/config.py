import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'temp', 'uploads')
    PROCESSED_FOLDER = os.path.join(BASE_DIR, 'temp', 'processed')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    # OCR Settings
    TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Default path for Windows
    
    # Redaction Settings
    RED_BOX_COLOR = (0, 0, 0) # Black for redaction
    
    # Ensure directories exist
    @staticmethod
    def init_app():
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.PROCESSED_FOLDER, exist_ok=True)
