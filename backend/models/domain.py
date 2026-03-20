from typing import List, Optional
from pydantic import BaseModel, Field

class InsightBase(BaseModel):
    """Base model for all AI generated insights requiring evidence and confidence."""
    evidence: str = Field(..., description="Exact quote or snippet from the source text confirming this insight")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence score for this specific insight")

class RiskFlag(InsightBase):
    indicator: str = Field(..., description="The medical indicator, e.g., 'Blood Sugar', 'Hemoglobin'")
    value: str = Field(..., description="The parsed value with units if any")
    status: str = Field(..., description="Risk status: Normal, Low, High, Critical")

class Medication(InsightBase):
    name: str = Field(..., description="Name of the medication")
    dosage: str = Field(..., description="Prescribed dosage")
    schedule: str = Field(..., description="Schedule (e.g., Twice daily, After meals)")

class SummaryInsight(InsightBase):
    summary: str = Field(..., description="A patient-friendly, easy to understand summary of the overall report")

class DoctorReport(InsightBase):
    clinical_impression: str = Field(..., description="Clinical impression suitable for a physician")
    plan: str = Field(..., description="Recommended medical plan or lifestyle modifications")

class MedicalDataExtraction(BaseModel):
    """The raw structured extraction from the OCR text."""
    lab_results: List[dict] = []
    medications: List[dict] = []
    demographics: dict = {}
    clinical_notes: str = ""
