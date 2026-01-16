"""
PDF text extraction module.
Uses PyPDF2 for reliable PDF text extraction.
"""
import io
from typing import Tuple
try:
    from PyPDF2 import PdfReader
except ImportError:
    try:
        import pypdf
        PdfReader = pypdf.PdfReader
    except ImportError:
        raise ImportError("Please install PyPDF2: pip install PyPDF2")


def extract_text_from_pdf(pdf_bytes: bytes) -> Tuple[str, int]:
    """
    Extract text from PDF bytes.
    
    Returns:
        Tuple[str, int]: (extracted_text, page_count)
    """
    try:
        pdf_data = io.BytesIO(pdf_bytes)
        pdf_reader = PdfReader(pdf_data)
        
        # Extract text from all pages
        text_parts = []
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        text = "\n\n".join(text_parts)
        page_count = len(pdf_reader.pages)
        
        if not text or len(text.strip()) == 0:
            raise ValueError("PDF appears to be empty or contains no extractable text")
        
        return text, page_count
    
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
