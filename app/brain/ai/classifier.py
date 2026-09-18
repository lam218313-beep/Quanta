"""
OCR and Document Classification Engine.
Extracts text from PDFs and images, classifies document type, and extracts fields.
"""
import re
from typing import Optional
from PIL import Image
import io


class DocumentClassifier:
    """Classifies documents and extracts structured data."""
    
    # Patterns for Peruvian documents
    PATTERNS = {
        'ruc': r'\b(10|20)\d{9}\b',  # RUC: 11 digits starting with 10 or 20
        'invoice_number': r'[FfBb]\d{3}[-\s]?\d{1,8}',  # F001-00001234 or B001-1234
        'amount': r'S/?\.?\s*[\d,]+\.?\d{0,2}',  # S/ 1,234.56
        'date': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY or similar
        'igv': r'IGV.*?[\d,]+\.?\d{0,2}',
        'detraccion': r'[Dd]etrac[cióni]+|SPOT',
        'banco': r'BCP|BBVA|Interbank|Scotiabank|BanBif',
        'operacion': r'[Oo]perac[ióni]+\s*#?\s*\d+|\d{6,12}',  # Operation number
    }
    
    # Keywords for classification
    DOC_KEYWORDS = {
        'invoice': ['factura', 'boleta', 'comprobante', 'ruc', 'igv', 'gravado', 'serie'],
        'voucher': ['voucher', 'transferencia', 'depósito', 'operación', 'cargo', 'abono', 'banco'],
        'receipt': ['recibo', 'suministro', 'agua', 'luz', 'teléfono', 'sedapal', 'enel'],
    }
    
    def classify_document(self, text: str) -> dict:
        """
        Classify document type based on text content.
        
        Returns:
            {"type": "invoice|voucher|receipt|unknown", "confidence": 0.0-1.0}
        """
        text_lower = text.lower()
        scores = {}
        
        for doc_type, keywords in self.DOC_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            scores[doc_type] = matches / len(keywords)
        
        if not scores or max(scores.values()) < 0.2:
            return {"type": "unknown", "confidence": 0.0}
        
        best_type = max(scores, key=scores.get)
        return {"type": best_type, "confidence": round(scores[best_type], 2)}
    
    def extract_invoice_fields(self, text: str) -> dict:
        """Extract fields from an invoice."""
        fields = {}
        
        # Extract RUC
        ruc_match = re.search(self.PATTERNS['ruc'], text)
        if ruc_match:
            fields['ruc'] = {
                'value': ruc_match.group(),
                'confidence': 0.95
            }
        
        # Extract invoice number
        inv_match = re.search(self.PATTERNS['invoice_number'], text, re.IGNORECASE)
        if inv_match:
            fields['invoice_number'] = {
                'value': inv_match.group().upper(),
                'confidence': 0.90
            }
        
        # Extract amounts
        amounts = re.findall(self.PATTERNS['amount'], text)
        if amounts:
            # Clean and sort amounts, largest is likely the total
            cleaned = []
            for amt in amounts:
                clean = re.sub(r'[^\d.,]', '', amt).replace(',', '')
                try:
                    cleaned.append(float(clean))
                except:
                    pass
            if cleaned:
                fields['total'] = {
                    'value': max(cleaned),
                    'confidence': 0.80
                }
        
        # Extract date
        date_match = re.search(self.PATTERNS['date'], text)
        if date_match:
            fields['date'] = {
                'value': date_match.group(),
                'confidence': 0.85
            }
        
        # Check for detraccion
        if re.search(self.PATTERNS['detraccion'], text, re.IGNORECASE):
            fields['has_detraccion'] = {
                'value': True,
                'confidence': 0.90
            }
        
        return fields
    
    def extract_voucher_fields(self, text: str) -> dict:
        """Extract fields from a bank voucher."""
        fields = {}
        
        # Detect bank
        bank_match = re.search(self.PATTERNS['banco'], text, re.IGNORECASE)
        if bank_match:
            fields['bank'] = {
                'value': bank_match.group().upper(),
                'confidence': 0.95
            }
        
        # Extract operation number
        op_match = re.search(self.PATTERNS['operacion'], text, re.IGNORECASE)
        if op_match:
            # Extract just the digits
            digits = re.search(r'\d+', op_match.group())
            if digits:
                fields['operation_number'] = {
                    'value': digits.group(),
                    'confidence': 0.85
                }
        
        # Extract amount
        amounts = re.findall(self.PATTERNS['amount'], text)
        if amounts:
            cleaned = []
            for amt in amounts:
                clean = re.sub(r'[^\d.,]', '', amt).replace(',', '')
                try:
                    cleaned.append(float(clean))
                except:
                    pass
            if cleaned:
                fields['amount'] = {
                    'value': max(cleaned),
                    'confidence': 0.80
                }
        
        # Extract date
        date_match = re.search(self.PATTERNS['date'], text)
        if date_match:
            fields['date'] = {
                'value': date_match.group(),
                'confidence': 0.85
            }
        
        return fields
    
    def process(self, text: str) -> dict:
        """
        Full processing pipeline: classify and extract fields.
        
        Returns:
            {
                "classification": {"type": "...", "confidence": 0.X},
                "extracted_data": {...}
            }
        """
        classification = self.classify_document(text)
        
        if classification['type'] == 'invoice':
            extracted = self.extract_invoice_fields(text)
        elif classification['type'] == 'voucher':
            extracted = self.extract_voucher_fields(text)
        else:
            extracted = {}
        
        return {
            "classification": classification,
            "extracted_data": extracted,
            "raw_text_preview": text[:500] if len(text) > 500 else text
        }


# Singleton instance
classifier = DocumentClassifier()


def get_classifier() -> DocumentClassifier:
    """Get the document classifier instance."""
    return classifier
