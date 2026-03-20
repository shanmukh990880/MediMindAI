import os
import json
import asyncio
from typing import List, Dict, Any
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPPipeline:
    def __init__(self):
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        if self.project_id:
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM with the given prompt."""
        if not self.model:
            logger.warning("Vertex AI not initialized. Using Mock response.")
            return await self._get_mock_response(prompt)
        
        try:
            # Running in executor for sync Vertex AI SDK
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.model.generate_content, prompt)
            return response.text
        except Exception as e:
            logger.error(f"LLM Call failed: {e}")
            return await self._get_mock_response(prompt)

    async def process(self, extracted_text: str) -> Dict[str, Any]:
        """Run the multi-step prompting pipeline."""
        
        # Step 1: Extraction (Text to Structured JSON)
        extraction_prompt = f"""
        Extract medical data from this text into structured details:
        Text: {extracted_text}
        Include:
        - Lab results (indicator, value, units, normal range)
        - Medications (name, dose, frequency)
        - Patient demographics (age, gender)
        - Clinical impression
        Return only JSON.
        """
        raw_extraction = await self._call_llm(extraction_prompt)
        structured_data = self._clean_json(raw_extraction)

        # Step 2: Parallel processing for Summaries, Risks, Timeline, and Doctor Report
        tasks = [
            self._generate_summary(structured_data),
            self._detect_risks(structured_data),
            self._generate_timeline(structured_data),
            self._generate_doctor_report(structured_data)
        ]
        
        summary, risks, timeline, doc_report = await asyncio.gather(*tasks)

        return {
            "summary": summary,
            "risk_flags": risks,
            "medication_timeline": timeline,
            "doctor_report": doc_report
        }

    async def _generate_summary(self, data: Dict) -> str:
        prompt = f"Based on this medical data, provide a simple, patient-friendly summary: {json.dumps(data)}"
        return await self._call_llm(prompt)

    async def _detect_risks(self, data: Dict) -> List[Dict]:
        prompt = f"""
        Identify any high/low/abnormal risk flags from this data: {json.dumps(data)}
        For each, provide: indicator, value, and status (Normal, High, Low, Critical).
        Return as a JSON list of objects.
        """
        raw = await self._call_llm(prompt)
        return self._clean_json(raw)

    async def _generate_timeline(self, data: Dict) -> List[Dict]:
        prompt = f"""
        Extract medication schedule and timeline from this data: {json.dumps(data)}
        For each, provide: name, dosage, and schedule (mornings, before meals, etc.).
        Return as a JSON list of objects.
        """
        raw = await self._call_llm(prompt)
        return self._clean_json(raw)

    async def _generate_doctor_report(self, data: Dict) -> str:
        prompt = f"Based on this medical data, generate a clinical report suitable for a physician: {json.dumps(data)}"
        return await self._call_llm(prompt)

    def _clean_json(self, raw: str) -> Any:
        try:
            # Basic markdown cleaning
            cleaned = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except Exception:
            return {}

    async def _get_mock_response(self, prompt: str) -> str:
        """Fallback mock responses for development/offline mode."""
        prompt_lower = prompt.lower()
        if "risk" in prompt_lower:
            return json.dumps([{"indicator": "Sugar", "value": "150", "status": "High"}])
        if "timeline" in prompt_lower or "medication" in prompt_lower:
            return json.dumps([{"name": "Metformin", "dosage": "500", "schedule": "Daily"}])
        if "summary" in prompt_lower:
            return "This is a mock patient-friendly summary of your medical report."
        if "doctor" in prompt_lower or "physician" in prompt_lower or "clinical" in prompt_lower:
            return "Clinical Impression: Normal except for slightly elevated glucose. Plan: Lifestyle modifications and follow-up in 3 months."
        if "extract" in prompt_lower or "json" in prompt_lower:
            return json.dumps({
                "lab_results": [{"indicator": "Sugar", "value": "150", "units": "mg/dL"}],
                "medications": [{"name": "Metformin", "dose": "500mg", "frequency": "Daily"}]
            })
        return "Medibrief AI Mock Report: Patient profile shows stable indicators for age and gender. No critical issues detected."
