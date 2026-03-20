import pytest
from backend.services.analysis_service import AnalysisService

@pytest.mark.asyncio
async def test_analysis_service_process_pipeline_mocked(mocker):
    """
    Tests the parallel pipeline orchestration by mocking the underlying Vertex AI client.
    Ensures that strictly typed Pydantic models (SummaryInsight, RiskFlag, etc.) are successfully inflated.
    """
    # Mock LLMClient
    mock_llm = mocker.patch("backend.services.analysis_service.LLMClient")
    
    # Configure mock returns for generate_json based on the prompt signature
    async def mock_generate_json(prompt, fallback):
        prompt_lower = prompt.lower()
        if "extract medical data from the following text" in prompt_lower:
            return {"lab_results": [], "medications": [{"name": "Aspirin"}], "clinical_notes": "test"}
        elif "summary" in prompt_lower:
            return {"summary": "Mock Summary", "evidence": "Mock Ev", "confidence_score": 0.99}
        elif "identify high/low" in prompt_lower or "risk" in prompt_lower:
            return [{"indicator": "Sugar", "value": "200", "status": "High", "evidence": "X", "confidence_score": 0.9}]
        elif "schedule" in prompt_lower or "timeline" in prompt_lower:
            return [{"name": "Aspirin", "dosage": "81mg", "schedule": "Daily", "evidence": "Y", "confidence_score": 0.9}]
        elif "clinical report" in prompt_lower or "physician" in prompt_lower:
            return {"clinical_impression": "Mock Imp", "plan": "Mock Plan", "evidence": "Z", "confidence_score": 0.9}
        return fallback


    mock_llm.return_value.generate_json.side_effect = mock_generate_json

    service = AnalysisService()
    result = await service.process_pipeline("Mock Extracted Text")

    # Assert Pydantic Models inflated correctly
    assert result["summary"].summary == "Mock Summary"
    assert result["summary"].confidence_score == 0.99
    assert len(result["risk_flags"]) == 1
    assert result["risk_flags"][0].indicator == "Sugar"
    assert len(result["medication_timeline"]) == 1
    assert result["doctor_report"].clinical_impression == "Mock Imp"
