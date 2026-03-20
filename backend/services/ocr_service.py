import io
import os
from google.cloud import documentai_v1 as documentai
from pdf2image import convert_from_bytes
import pytesseract
import logging
from pypdf import PdfReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us")
        self.processor_id = os.environ.get("DOCUMENT_AI_PROCESSOR_ID")

    async def extract_text(self, file_content: bytes) -> str:
        """Extract text using Google Document AI, with pypdf and Tesseract fallbacks."""
        # 1. Try Google Document AI
        if self.processor_id:
            try:
                return await self._extract_with_document_ai(file_content)
            except Exception as e:
                logger.error(f"Document AI failed: {e}. Falling back to pypdf.")
        
        # 2. Try pypdf (Lightweight, good for digital PDFs)
        text = await self._extract_with_pypdf(file_content)
        if text.strip():
            return text

        # 3. Try Tesseract (Heavier, for scanned image-based PDFs)
        logger.info("pypdf extracted no text. Falling back to Tesseract OCR.")
        return await self._extract_with_tesseract(file_content)

    async def _extract_with_document_ai(self, file_content: bytes) -> str:
        client = documentai.DocumentProcessorServiceClient()
        name = client.processor_path(self.project_id, self.location, self.processor_id)

        raw_document = documentai.RawDocument(content=file_content, mime_type="application/pdf")
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)

        result = client.process_document(request=request)
        return result.document.text

    async def _extract_with_pypdf(self, file_content: bytes) -> str:
        """Extract text from digital PDF using pypdf."""
        try:
            reader = PdfReader(io.BytesIO(file_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"pypdf extraction failed: {e}")
            return ""

    async def _extract_with_tesseract(self, file_content: bytes) -> str:
        """Fallback OCR using Tesseract (requires poppler and tesseract binaries)."""
        try:
            images = convert_from_bytes(file_content)
            full_text = ""
            for img in images:
                full_text += pytesseract.image_to_string(img) + "\n"
            return full_text
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}. Ensure poppler and tesseract are installed.")
            return ""
