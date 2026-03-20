from pydantic import BaseModel
from typing import List
from backend.models.domain import RiskFlag, Medication, SummaryInsight, DoctorReport

class ErrorResponse(BaseModel):
    detail: str

class SimplificationResponse(BaseModel):
    id: str
    summary: SummaryInsight
    risk_flags: List[RiskFlag]
    medication_timeline: List[Medication]
    doctor_report: DoctorReport
