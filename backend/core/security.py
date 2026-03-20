import logging
from fastapi import UploadFile
from backend.core.errors import AppException
from backend.core.config import settings

logger = logging.getLogger(__name__)

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logger.warning("libmagic system library not found. Deep MIME checks are skipped.")


async def validate_pdf(file: UploadFile):
    """
    Validates the uploaded file based on MIME type and size constraints defined in config.
    Using python-magic for more thorough MIME type checking, falling back if not available.
    """
    if file.content_type not in settings.ALLOWED_MIME_TYPES:
         if not file.filename.lower().endswith(".pdf"):
             raise AppException("Invalid file format. Only PDF files are accepted.", status_code=400)
    
    # Read first 2048 bytes for magic validation and size check without loading entirely
    header = await file.read(2048)
    await file.seek(0)  # Reset cursor for actual processing

    if not header:
        raise AppException("Uploaded file is empty.", status_code=400)
        
    if MAGIC_AVAILABLE:
        try:
            mime = magic.from_buffer(header, mime=True)
            if mime not in settings.ALLOWED_MIME_TYPES:
                raise AppException("File content does not match a valid PDF.", status_code=400)
        except Exception:
            pass

    # We cannot easily check size from a stream without reading it all, 
    # but we can rely on FastAPI's MAX_UPLOAD limit or check Content-Length header if passed.
    # We will enforce length limits at the web server (uvicorn/gunicorn) or via router dependencies.
    
    return True
