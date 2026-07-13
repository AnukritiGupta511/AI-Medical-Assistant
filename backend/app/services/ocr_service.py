import os
import fitz  # PyMuPDF
from typing import Optional
from fastapi import UploadFile

class OCRService:
    def __init__(self):
        pass

    async def extract_text(self, file_path: str, file_type: str) -> str:
        """
        Extracts text from a given PDF file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        extracted_text = ""

        try:
            if file_type in ['image/jpeg', 'image/png', 'image/jpg']:
                raise ValueError("Image OCR is disabled in Vercel Deployment mode. Please upload standard PDFs only.")
            elif file_type == 'application/pdf':
                extracted_text = self._extract_from_pdf(file_path)
            else:
                raise ValueError(f"Unsupported file type for OCR: {file_type}")
        except Exception as e:
            print(f"OCR Error: {str(e)}")
            raise e

        return extracted_text.strip()

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF exclusively."""
        text = ""
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            text += page_text + "\n"
        return text

ocr_service = OCRService()
