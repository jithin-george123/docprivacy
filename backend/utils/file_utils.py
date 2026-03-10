import os
import uuid
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PIL import Image

def get_unique_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}"

def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

def convert_pdf_to_images(pdf_path, output_folder):
    """
    Converts each page of a PDF to an image and returns the list of paths.
    """
    # Create a unique subfolder for this conversion
    session_id = uuid.uuid4().hex
    session_folder = os.path.join(output_folder, session_id)
    os.makedirs(session_folder, exist_ok=True)
    
    pages = convert_from_path(pdf_path)
    image_paths = []
    
    for i, page in enumerate(pages):
        filename = f"page_{i+1}.png"
        path = os.path.join(session_folder, filename)
        page.save(path, 'PNG')
        image_paths.append(path)
        
    return image_paths, session_id

def cleanup_file(filepath):
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass
