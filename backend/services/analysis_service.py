import json
import asyncio
from typing import Dict, Any
from backend.services.llm_client import LLMClient
from backend.models.domain import SummaryInsight, RiskFlag, Medication, DoctorReport

class AnalysisService:
    def __init__(self):
        self.llm = LLMClient("gemini-1.5-flash")

    async def _extract_raw(self, text: str) -> dict:
        prompt = f"""
        Extract medical data from the following text into structured JSON.
        DO NOT hallucinate. Answer ONLY based on the text.
        Required JSON Schema:
        {{
            "lab_results": [{{"indicator": "str", "value": "str", "units": "str"}}],
            "medications": [{{"name": "str", "dose": "str", "frequency": "str"}}],
            "clinical_notes": "str"
        }}
        Text: {text}
        """
        fallback_data = {"lab_results": [], "medications": [], "clinical_notes": ""}
        return await self.llm.generate_json(prompt, fallback_data)

    async def _generate_summary(self, data: dict) -> SummaryInsight:
        prompt = f"""
        Provide a patient-friendly summary of this medical data.
        DO NOT hallucinate.
        You must output valid JSON matching this exact schema:
        {{
            "summary": "Patient friendly summary",
            "evidence": "Exact quote from text confirming this",
            "confidence_score": 0.95
        }}
        Data: {json.dumps(data)}
        """
        fallback = {"summary": "Unable to generate summary in offline mode.", "evidence": "N/A", "confidence_score": 0.0}
        res = await self.llm.generate_json(prompt, fallback)
        # Ensure it maps to schema even if slightly modified
        if "confidence_score" not in res: res["confidence_score"] = 0.5
        if "evidence" not in res: res["evidence"] = "System generated."
        return SummaryInsight(**res)

    async def _detect_risks(self, data: dict) -> list[RiskFlag]:
        prompt = f"""
        Identify high/low/abnormal risk flags from this data.
        DO NOT hallucinate.
        You must output valid JSON matching this exact schema (an array of dicts):
        [{{
            "indicator": "Blood Sugar",
            "value": "150",
            "status": "High",
            "evidence": "Quote confirming this",
            "confidence_score": 0.90
        }}]
        Data: {json.dumps(data)}
        """
        fallback = [{"indicator": "Sample Risk", "value": "N/A", "status": "Unknown", "evidence": "Mock Data", "confidence_score": 0.0}]
        res = await self.llm.generate_json(prompt, fallback)
        try:
            return [RiskFlag(**item) for item in res] if isinstance(res, list) else []
        except Exception:
            return []

    async def _generate_timeline(self, data: dict) -> list[Medication]:
        prompt = f"""
        Extract medication schedule from this data.
        DO NOT hallucinate.
        You must output valid JSON matching this exact schema (an array of dicts):
        [{{
            "name": "Metformin",
            "dosage": "500",
            "schedule": "Daily",
            "evidence": "Quote",
            "confidence_score": 0.9
        }}]
        Data: {json.dumps(data)}
        """
        fallback = [{"name": "Sample Med", "dosage": "N/A", "schedule": "Unknown", "evidence": "Mock Data", "confidence_score": 0.0}]
        res = await self.llm.generate_json(prompt, fallback)
        try:
            return [Medication(**item) for item in res] if isinstance(res, list) else []
        except Exception:
            return []

    async def _generate_doctor_report(self, data: dict) -> DoctorReport:
        prompt = f"""
        Generate a clinical report suitable for a physician based on the data.
        DO NOT hallucinate.
        You must output valid JSON matching this exact schema:
        {{
            "clinical_impression": "Impression",
            "plan": "Plan",
            "evidence": "Quote",
            "confidence_score": 0.95
        }}
        Data: {json.dumps(data)}
        """
        fallback = {"clinical_impression": "Offline mock impression", "plan": "N/A", "evidence": "N/A", "confidence_score": 0.0}
        res = await self.llm.generate_json(prompt, fallback)
        if "confidence_score" not in res: res["confidence_score"] = 0.5
        if "evidence" not in res: res["evidence"] = "System generated."
        return DoctorReport(**res)

    async def process_pipeline(self, extracted_text: str) -> Dict[str, Any]:
        """Orchestrates the parallel LLM generation tasks."""
        structured_data = await self._extract_raw(extracted_text)

        summary_task = self._generate_summary(structured_data)
        risks_task = self._detect_risks(structured_data)
        timeline_task = self._generate_timeline(structured_data)
        doc_report_task = self._generate_doctor_report(structured_data)

        summary, risk_flags, timeline, doctor_report = await asyncio.gather(
            summary_task, risks_task, timeline_task, doc_report_task
        )

        return {
            "summary": summary,
            "risk_flags": risk_flags,
            "medication_timeline": timeline,
            "doctor_report": doctor_report
        }
