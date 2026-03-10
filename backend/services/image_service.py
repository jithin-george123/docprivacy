from PIL import Image, ImageDraw
import numpy as np
import cv2
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class ImageService:
    @staticmethod
    def apply_masks(image_path, masks, output_path):
        """
        Applies a list of masks (rectangle regions) to an image.
        """
        # Load image via Pillow or OpenCV (Pillow preferred for drawing)
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        for mask in masks:
            # mask: {'x': 100, 'y': 200, 'w': 50, 'h': 20}
            x, y, w, h = mask['x'], mask['y'], mask['w'], mask['h']
            draw.rectangle([x, y, x + w, y + h], fill="black")
            
        img.save(output_path)
        return output_path

    @staticmethod
    def save_as_pdf(masked_image_paths, output_pdf_path):
        """
        Converts a list of images into a single PDF.
        """
        c = canvas.Canvas(output_pdf_path, pagesize=letter)
        
        for img_path in masked_image_paths:
            img = Image.open(img_path)
            width, height = img.size
            
            # Match the page size to the image size (points)
            # Default to letter if size is strange or huge
            # Adjust to fits letter size for printing if needed
            c.setPageSize((width, height))
            c.drawImage(img_path, 0, 0, width, height)
            c.showPage()
            
        c.save()
        return output_pdf_path
