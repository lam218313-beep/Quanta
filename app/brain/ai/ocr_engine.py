"""
OCR Engine - Text extraction from PDFs and images.
Uses pytesseract (Tesseract OCR) as the primary engine.
Falls back to pypdf for text-based PDFs.
"""
import io
from typing import Optional
from PIL import Image


class OCREngine:
    """Extracts text from images and PDFs."""
    
    def __init__(self):
        self._tesseract_available = None
        self._poppler_available = None
    
    def _check_tesseract(self) -> bool:
        """Check if Tesseract is available."""
        if self._tesseract_available is None:
            try:
                import pytesseract
                # Try to get version to confirm it's working
                pytesseract.get_tesseract_version()
                self._tesseract_available = True
            except Exception:
                self._tesseract_available = False
        return self._tesseract_available
    
    def _check_poppler(self) -> bool:
        """Check if Poppler (pdf2image) is available."""
        if self._poppler_available is None:
            try:
                from pdf2image import convert_from_bytes
                self._poppler_available = True
            except Exception:
                self._poppler_available = False
        return self._poppler_available
    
    def extract_from_image(self, image_bytes: bytes) -> str:
        """Extract text from an image using Tesseract OCR."""
        if not self._check_tesseract():
            return "[OCR not available - Tesseract not installed]"
        
        try:
            import pytesseract
            image = Image.open(io.BytesIO(image_bytes))
            # Use Spanish language for better recognition of Peruvian documents
            text = pytesseract.image_to_string(image, lang='spa')
            return text.strip()
        except Exception as e:
            return f"[OCR error: {e}]"
    
    def extract_from_pdf(self, pdf_bytes: bytes) -> str:
        """
        Extract text from a PDF.
        First tries pypdf (for text-based PDFs), then falls back to OCR.
        If OCR fails (Poppler not installed), tries to decode as plain text.
        """
        # Try text extraction first (faster for text-based PDFs)
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text_parts = []
            for page in reader.pages[:5]:  # Limit to first 5 pages
                text_parts.append(page.extract_text() or "")
            text = "\n".join(text_parts).strip()
            
            # If we got meaningful text, use it
            if len(text) > 100:
                return text
        except Exception as e:
            print(f"   [pypdf failed: {e}]")
        
        # Try OCR if available (for scanned PDFs)
        if self._check_poppler() and self._check_tesseract():
            try:
                from pdf2image import convert_from_bytes
                import pytesseract
                
                # Convert PDF pages to images
                images = convert_from_bytes(pdf_bytes, first_page=1, last_page=3)
                
                text_parts = []
                for img in images:
                    text = pytesseract.image_to_string(img, lang='spa')
                    text_parts.append(text)
                
                return "\n".join(text_parts).strip()
            except Exception as e:
                print(f"   [PDF OCR failed: {e}]")
        
        # Final fallback: try to decode as plain text (for text files uploaded as PDF)
        try:
            text = pdf_bytes.decode('utf-8')
            if len(text.strip()) > 50:
                print(f"   [Decoded as plain text]")
                return text.strip()
        except:
            pass
        
        try:
            text = pdf_bytes.decode('latin-1')
            if len(text.strip()) > 50:
                print(f"   [Decoded as latin-1 text]")
                return text.strip()
        except:
            pass
        
        return "[PDF extraction failed - content type may be incorrect or Poppler not installed]"
    
    def extract(self, file_bytes: bytes, content_type: str) -> str:
        """
        Extract text based on content type.
        
        Args:
            file_bytes: Raw file content
            content_type: MIME type (application/pdf, image/jpeg, etc.)
        
        Returns:
            Extracted text
        """
        if content_type == 'application/pdf':
            return self.extract_from_pdf(file_bytes)
        elif content_type in ['image/jpeg', 'image/png', 'image/jpg']:
            return self.extract_from_image(file_bytes)
        elif content_type in ['text/xml', 'application/xml']:
            # XML files are already text, just decode
            try:
                return file_bytes.decode('utf-8')
            except:
                return file_bytes.decode('latin-1', errors='ignore')
        else:
            return f"[Unsupported content type: {content_type}]"


# Singleton
_ocr_engine: Optional[OCREngine] = None


def get_ocr() -> OCREngine:
    """Get or create OCR engine singleton."""
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = OCREngine()
    return _ocr_engine
