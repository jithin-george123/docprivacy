from flask import Flask, send_from_directory
from flask_cors import CORS
import os
import pytesseract
from backend.config import Config
from backend.routes.redaction import redaction_bp

def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    CORS(app)
    
    # Configure Pytesseract path for Windows (if not in PATH)
    if os.path.exists(Config.TESSERACT_CMD):
        pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD
    
    # Register blueprints
    app.register_blueprint(redaction_bp, url_prefix='/api')
    
    # Initialize directories
    Config.init_app()
    
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', debug=True, port=5000)
