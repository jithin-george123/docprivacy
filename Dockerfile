FROM python:3.9-slim

# Install system dependencies for OCR, PDF processing, and OpenCV
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 5000

# Set PYTHONPATH so 'backend' module is found
ENV PYTHONPATH="."

# Run the application
CMD ["python", "backend/app.py"]
