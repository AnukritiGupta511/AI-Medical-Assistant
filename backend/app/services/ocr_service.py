import os
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from typing import Optional
from fastapi import UploadFile

class OCRService:
    def __init__(self):
        # Allow configuring Tesseract path if needed, e.g., for Windows
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass

    async def extract_text(self, file_path: str, file_type: str) -> str:
        """
        Extracts text from a given image or PDF file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        extracted_text = ""

        try:
            if file_type in ['image/jpeg', 'image/png', 'image/jpg']:
                extracted_text = self._extract_from_image(file_path)
            elif file_type == 'application/pdf':
                extracted_text = self._extract_from_pdf(file_path)
            else:
                raise ValueError(f"Unsupported file type for OCR: {file_type}")
        except Exception as e:
            # Add logging here in production
            print(f"OCR Error: {str(e)}")
            raise e

        return extracted_text.strip()

    def _extract_from_image(self, file_path: str) -> str:
        """Extract text from an image using Tesseract."""
        image = Image.open(file_path)
        # Apply basic preprocessing if necessary (grayscale, thresholding)
        text = pytesseract.image_to_string(image)
        return text

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF. If it's a scanned PDF, apply OCR to pages."""
        text = ""
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            
            # If no text is found, it might be a scanned PDF. Use OCR on page image.
            if not page_text.strip():
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                page_text = pytesseract.image_to_string(img)
                
            text += page_text + "\n"
        return text

ocr_service = OCRService()
