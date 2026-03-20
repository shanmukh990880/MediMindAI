import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uuid

# Internal imports
from backend.services.ocr_service import OCRService
from backend.services.mcp_pipeline import MCPPipeline
from backend.utils.security import validate_pdf
from backend.utils.cache import get_cached_result, set_cached_result

app = FastAPI(title="MediBrief AI API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Medication(BaseModel):
    name: str
    dosage: str
    schedule: str

class RiskFlag(BaseModel):
    indicator: str
    value: str
    status: str  # e.g., "High", "Low", "Normal"

class SimplificationResponse(BaseModel):
    id: str
    summary: str
    risk_flags: List[RiskFlag]
    medication_timeline: List[Medication]
    doctor_report: str

@app.get("/api/health")
async def health():
    return {"message": "MediBrief AI API is running"}

@app.post("/simplify", response_model=SimplificationResponse)
async def simplify_report(file: UploadFile = File(...)):
    # 1. Validate File
    await validate_pdf(file)
    
    # Generate unique ID for this request
    request_id = str(uuid.uuid4())
    
    # 2. Extract Text (OCR)
    file_content = await file.read()
    
    # Check cache first (using content hash or similar, for now placeholder)
    cached = get_cached_result(file_content)
    if cached:
        return cached

    ocr_service = OCRService()
    extracted_text = await ocr_service.extract_text(file_content)
    
    if not extracted_text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    # 3. Process through MCP Pipeline
    pipeline = MCPPipeline()
    result = await pipeline.process(extracted_text)
    
    response = SimplificationResponse(
        id=request_id,
        summary=result["summary"],
        risk_flags=result["risk_flags"],
        medication_timeline=result["medication_timeline"],
        doctor_report=result["doctor_report"]
    )
    
    # Cache result
    set_cached_result(file_content, response.dict())
    
    return response

# Serve static files for frontend after all API routes
frontend_dist = os.environ.get("FRONTEND_DIST")
if frontend_dist and os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
