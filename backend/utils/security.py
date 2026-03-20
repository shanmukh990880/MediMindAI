from fastapi import UploadFile, HTTPException
import bleach

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

async def validate_pdf(file: UploadFile):
    """Validate file type and size."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Check size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")

def sanitize_text(text: str) -> str:
    """Sanitize extracted text for security."""
    return bleach.clean(text, tags=[], strip=True)
