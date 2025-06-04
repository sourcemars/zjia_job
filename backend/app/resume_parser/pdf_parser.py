"""
PDF parser for extracting text from PDF files.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PDFParser:
    """Parser for PDF documents."""
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text content from a PDF document.
        
        Args:
            file_path: Path to the PDF document
            
        Returns:
            Extracted text content
            
        Raises:
            ImportError: If required libraries are not installed
            Exception: If file cannot be read
        """
        try:
            return self._extract_with_pypdf2(file_path)
        except ImportError:
            logger.warning("PyPDF2 not available, trying pdfplumber")
            try:
                return self._extract_with_pdfplumber(file_path)
            except ImportError:
                logger.warning("pdfplumber not available, trying textract")
                return self._extract_with_textract(file_path)
        except Exception as e:
            logger.warning(f"PyPDF2 failed for {file_path}: {e}, trying alternatives")
            try:
                return self._extract_with_pdfplumber(file_path)
            except Exception as e2:
                logger.warning(f"pdfplumber also failed: {e2}, trying textract")
                return self._extract_with_textract(file_path)
    
    def _extract_with_pypdf2(self, file_path: str) -> str:
        """Extract text using PyPDF2."""
        try:
            import PyPDF2
        except ImportError:
            raise ImportError("PyPDF2 library is required. Install with: pip install PyPDF2")
        
        try:
            text_content = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(text.strip())
            
            return '\n'.join(text_content)
            
        except Exception as e:
            logger.error(f"Error reading PDF with PyPDF2 {file_path}: {e}")
            raise
    
    def _extract_with_pdfplumber(self, file_path: str) -> str:
        """Extract text using pdfplumber (better for complex layouts)."""
        try:
            import pdfplumber
        except ImportError:
            raise ImportError("pdfplumber library is required. Install with: pip install pdfplumber")
        
        try:
            text_content = []
            
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and text.strip():
                        text_content.append(text.strip())
            
            return '\n'.join(text_content)
            
        except Exception as e:
            logger.error(f"Error reading PDF with pdfplumber {file_path}: {e}")
            raise
    
    def _extract_with_textract(self, file_path: str) -> str:
        """Extract text using textract (handles many formats)."""
        try:
            import textract
        except ImportError:
            raise ImportError("textract library is required. Install with: pip install textract")
        
        try:
            text = textract.process(file_path).decode('utf-8')
            return text.strip() if text else ""
            
        except Exception as e:
            logger.error(f"Error reading PDF with textract {file_path}: {e}")
            raise
