import uuid
from fastapi import APIRouter, UploadFile, File, Request
from backend.models.api import SimplificationResponse
from backend.core.security import validate_pdf
from backend.core.errors import AppException
from backend.services.ocr_service import OCRService
from backend.services.analysis_service import AnalysisService
from backend.core.rate_limiter import limiter

router = APIRouter()

@router.post("/simplify", response_model=SimplificationResponse, tags=["pdf"])
@limiter.limit("10/minute")
async def simplify_report(request: Request, file: UploadFile = File(...)):
    await validate_pdf(file)
    
    file_content = await file.read()
    request_id = str(uuid.uuid4())

    ocr_service = OCRService()
    extracted_text = await ocr_service.extract_text(file_content)
    if not extracted_text:
        raise AppException("Could not extract any text from the provided PDF.", status_code=400)

    # Future: Offload to Cloud Tasks
    analysis_service = AnalysisService()
    result = await analysis_service.process_pipeline(extracted_text)
    
    try:
        response = SimplificationResponse(
            id=request_id,
            summary=result["summary"],
            risk_flags=result["risk_flags"],
            medication_timeline=result["medication_timeline"],
            doctor_report=result["doctor_report"]
        )
    except Exception as e:
        raise AppException(f"Failed to map AI output to strict schema: {e}", status_code=500)
    
    return response
