# Document Privacy Masking Tool

A secure, web-based tool for redacting sensitive information (Aadhaar, PAN) from documents before sharing.

## Features
- **File Support**: JPG, PNG, and PDF.
- **Auto-Detection**: OCR-based pattern matching for Indian identifiers (PAN, Aadhaar).
- **Interactive Redaction**: Suggests masks for common identifiers or allows manual drawing.
- **Privacy First**: No database, no persistent storage, and stateless processing.
- **Export**: Generates permanent masked PDFs.

## Architecture
- **Frontend**: Vanilla JavaScript + HTML5 Canvas API for interactive redaction and client-side preview.
- **Backend**: Python/Flask with:
  - `pytesseract` for text extraction and bounding box detection.
  - `pdf2image` for converting PDF pages to processable image frames.
  - `reportlab` for generating the final sanitized PDF.
  - `Pillow` for image manipulation and mask application.

## Prerequisites
1. **Python 3.8+**
2. **Tesseract OCR**: You must have Tesseract installed on your system.
   - [Windows Install Guide](https://github.com/UB-Mannheim/tesseract/wiki)
   - [Linux/Mac Install Guide](https://tesseract-ocr.github.io/tessdoc/Installation.html)
3. **Poppler**: Required by `pdf2image`.
   - Windows: [Download Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases) and add the `bin` folder to your PATH.

## Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Update the `TESSERACT_CMD` path in `backend/config.py` if your Tesseract installation is in a custom folder.

## Running the App
1. Start the Flask server:
   ```bash
   python backend/app.py
   ```
2. Navigate to `http://localhost:5000` in your web browser.

## Directory Structure
```
document-privacy-masking/
  backend/            # Flask API, routing, and services
  frontend/           # HTML, CSS, and Vanilla JS
  docs/               # Documentation
  requirements.txt    # Python dependencies
  README.md           # Project documentation
```

## Privacy Notice
This application is designed for local privacy. Files uploaded are stored in a temporary folder and are deleted (or not persisted) after the session ends. No document content is logged or shared.
