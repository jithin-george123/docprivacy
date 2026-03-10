import pytesseract
from PIL import Image
import re
import numpy as np
import cv2
from backend.config import Config

# Ensure pytesseract knows the path
# (Assuming the path from Config is set up correctly in app.py)
# pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD

class OCRService:
    @staticmethod
    def preprocess_image(image_path):
        """
        Preprocesses an image to improve OCR accuracy.
        """
        img = cv2.imread(image_path)
        if img is None:
            return None
        # Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    @staticmethod
    def extract_text(image_path):
        """
        Extracts text and returns OCR result with bounding boxes with preprocessing.
        """
        preprocessed = OCRService.preprocess_image(image_path)
        if preprocessed is not None:
            img = Image.fromarray(preprocessed)
        else:
            img = Image.open(image_path)

        try:
            ocr_data = pytesseract.image_to_data(img, config='--oem 3 --psm 3', output_type=pytesseract.Output.DICT)
            return ocr_data
        except Exception as e:
            print(f"OCR Error: {e}")
            return None

    @staticmethod
    def detect_senstive_regions(ocr_data):
        """
        Identifies PII patterns (Aadhaar, PAN, Phone, Email) and suggests bounding boxes.
        """
        if not ocr_data:
            return []
            
        # Expanded Patterns
        patterns = {
            'Aadhaar': re.compile(r'\b\d{4}[ -]?\d{4}[ -]?\d{4}\b'),
            'PAN': re.compile(r'\b[A-Za-z]{5}[0-9]{4}[A-Za-z]\b'),
            'Phone': re.compile(r'\b(\+91[\s-]?)?[6789]\d{9}\b'),
            'Email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        }
        
        detected_items = []
        n_boxes = len(ocr_data['text'])
        handled = [False] * n_boxes
        
        for i in range(n_boxes):
            if handled[i]: continue
            text = str(ocr_data['text'][i]).strip()
            if not text: continue
            
            # Check most patterns
            found = False
            for p_type, pattern in patterns.items():
                match = pattern.search(text)
                if match:
                    detected_items.append({
                        'type': p_type,
                        'bbox': {
                            'x': ocr_data['left'][i], 'y': ocr_data['top'][i],
                            'w': ocr_data['width'][i], 'h': ocr_data['height'][i]
                        },
                        'text': match.group(),
                        'suggested_mask': "XXXX" if p_type != 'Email' else "X" * len(match.group())
                    })
                    handled[i] = True
                    found = True
                    break
            
            if found: continue

            # Handle multipart Aadhaar
            if re.fullmatch(r'\d{4}', text) and i+2 < n_boxes:
                t2, t3 = str(ocr_data['text'][i+1]).strip(), str(ocr_data['text'][i+2]).strip()
                combined = f"{text} {t2} {t3}"
                if re.fullmatch(r'\d{4} \d{4} \d{4}', combined):
                    x = ocr_data['left'][i]
                    y = min(ocr_data['top'][i], ocr_data['top'][i+1], ocr_data['top'][i+2])
                    w = (ocr_data['left'][i+2] + ocr_data['width'][i+2]) - x
                    h = max(ocr_data['height'][i], ocr_data['height'][i+1], ocr_data['height'][i+2])
                    detected_items.append({
                        'type': 'Aadhaar',
                        'bbox': {'x': x, 'y': y, 'w': w, 'h': h},
                        'text': combined,
                        'suggested_mask': "XXXX XXXX " + combined[-4:]
                    })
                    handled[i] = handled[i+1] = handled[i+2] = True

        return detected_items
