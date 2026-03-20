import pytest
from fastapi import UploadFile
from backend.core.security import validate_pdf
from backend.core.errors import AppException
import io

@pytest.mark.asyncio
async def test_validate_pdf_valid_extension():
    """Test that a basic PDF extension bypasses strict MIME failing."""
    # We spoof the content_type and filename to mimic FastAPI's UploadFile
    file = UploadFile(filename="test.pdf", file=io.BytesIO(b"%PDF-1.4\nTest data strictly mocked for magic fallback"))
    
    # Manually override content_type since UploadFile constructor relies on starlette's guessing
    file.headers = {"content-type": "application/pdf"}
    
    result = await validate_pdf(file)
    assert result is True

@pytest.mark.asyncio
async def test_validate_pdf_invalid_extension():
    """Test that non-PDF extensions raise a 400."""
    file = UploadFile(filename="test.png", file=io.BytesIO(b"fake png data"))
    
    with pytest.raises(AppException) as exc:
        await validate_pdf(file)
    assert exc.value.status_code == 400
    assert "Invalid file format" in exc.value.message

@pytest.mark.asyncio
async def test_validate_empty_file():
    """Test that empty files are rejected."""
    file = UploadFile(filename="test.pdf", file=io.BytesIO(b""))
    
    with pytest.raises(AppException) as exc:
        await validate_pdf(file)
    assert exc.value.status_code == 400
    assert "empty" in exc.value.message.lower()
