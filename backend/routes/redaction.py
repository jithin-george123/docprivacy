from flask import Blueprint, request, jsonify, send_from_directory, url_for
from werkzeug.utils import secure_filename
import os
import uuid
import shutil
from backend.config import Config
from backend.utils.file_utils import get_unique_filename, allowed_file, convert_pdf_to_images, cleanup_file
from backend.services.ocr_service import OCRService
from backend.services.image_service import ImageService
from PIL import Image

redaction_bp = Blueprint('redaction', __name__)

# Keep tracked status in-memory for session-like behavior (no DB)
# For a production app, we'd use a more robust way to track files per ID
# sessions = { session_id: { images: [], masks: [], original_path: '' } }
sessions = {}

@redaction_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
        filename = secure_filename(file.filename)
        unique_name = get_unique_filename(filename)
        upload_path = os.path.join(Config.UPLOAD_FOLDER, unique_name)
        file.save(upload_path)
        
        # Determine if it's a PDF
        is_pdf = filename.lower().endswith('.pdf')
        session_id = uuid.uuid4().hex
        
        if is_pdf:
            # Convert PDF pages to images
            image_paths, session_id_sub = convert_pdf_to_images(upload_path, Config.UPLOAD_FOLDER)
            session_id = session_id_sub
            images = [os.path.basename(p) for p in image_paths]
            
            # Sub-folder is images' relative base
            images = [f"{session_id}/{img}" for img in images]
            
            sessions[session_id] = {
                'original_path': upload_path,
                'image_paths': image_paths,
                'masks': [[] for _ in image_paths], # One list of masks per page
                'type': 'PDF'
            }
        else:
            # Image handling
            session_id = uuid.uuid4().hex
            image_paths = [upload_path]
            images = [unique_name]
            
            sessions[session_id] = {
                'original_path': upload_path,
                'image_paths': image_paths,
                'masks': [[]],
                'type': 'IMAGE'
            }
            
        return jsonify({
            'session_id': session_id,
            'images': images,
            'message': 'File uploaded successfully'
        })
        
    return jsonify({'error': 'File type not allowed'}), 400

@redaction_bp.route('/detect', methods=['POST'])
def detect_sensitive():
    data = request.json
    session_id = data.get('session_id')
    page_index = data.get('page_index', 0)
    
    if session_id not in sessions:
        return jsonify({'error': 'Invalid session'}), 404
        
    image_path = sessions[session_id]['image_paths'][page_index]
    
    # Run OCR
    try:
        ocr_data = OCRService.extract_text(image_path)
        detections = OCRService.detect_senstive_regions(ocr_data)
        
        return jsonify({
            'page_index': page_index,
            'detections': detections
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@redaction_bp.route('/redact', methods=['POST'])
def redact_and_download():
    data = request.json
    session_id = data.get('session_id')
    pages_masks = data.get('masks') # List of list of masks: [[{x,y,w,h}...], [...]]
    
    if session_id not in sessions:
        return jsonify({'error': 'Invalid session'}), 404
        
    session = sessions[session_id]
    original_images = session['image_paths']
    
    masked_images = []
    
    for i, image_path in enumerate(original_images):
        masks = pages_masks[i] if i < len(pages_masks) else []
        
        # New filename for masked version
        masked_filename = f"masked_{i}_{uuid.uuid4().hex}.png"
        masked_path = os.path.join(Config.PROCESSED_FOLDER, masked_filename)
        
        # Apply masks
        ImageService.apply_masks(image_path, masks, masked_path)
        masked_images.append(masked_path)
        
    # Generate PDF
    output_pdf_name = f"redacted_{uuid.uuid4().hex}.pdf"
    output_pdf_path = os.path.join(Config.PROCESSED_FOLDER, output_pdf_name)
    
    # Save as single PDF
    ImageService.save_as_pdf(masked_images, output_pdf_path)
    
    # Return path relative for serving if needed, although usually we want direct stream
    return jsonify({
        'download_url': f"/api/download/{output_pdf_name}"
    })

@redaction_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # This is where we could clean up the files after serving them.
    # In a stateless environment, we can set a timer or check after response.
    return send_from_directory(Config.PROCESSED_FOLDER, filename, as_attachment=True)

@redaction_bp.route('/images/<path:filename>', methods=['GET'])
def serve_image(filename):
    # Support for served from session directories if needed
    return send_from_directory(Config.UPLOAD_FOLDER, filename)
