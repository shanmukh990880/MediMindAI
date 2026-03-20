import pytest
import json
from unittest.mock import AsyncMock, patch
from services.mcp_pipeline import MCPPipeline

@pytest.fixture
def mcp_pipeline():
    with patch("vertexai.init"):
        return MCPPipeline()

@pytest.mark.asyncio
async def test_mcp_pipeline_process(mcp_pipeline):
    # Mock LLM responses for each step
    mock_responses = {
        "Extract medical data": json.dumps({
            "lab_results": [{"indicator": "Sugar", "value": "150", "units": "mg/dL", "status": "High"}]
        }),
        "simple, patient-friendly summary": "Your sugar level is slightly high.",
        "identify any high/low/abnormal risk flags": json.dumps([{"indicator": "Sugar", "value": "150", "status": "High"}]),
        "Extract medication schedule": json.dumps([{"name": "Metformin", "dosage": "500mg", "schedule": "Daily"}]),
        "generate a clinical report": "Clinical impression: Elevated blood glucose."
    }

    async def side_effect(prompt):
        for key, val in mock_responses.items():
            if key in prompt:
                return val
        return "{}"

    mcp_pipeline._call_llm = AsyncMock(side_effect=side_effect)

    result = await mcp_pipeline.process("Sample OCR Text")

    assert "summary" in result
    assert "risk_flags" in result
    assert "medication_timeline" in result
    assert "doctor_report" in result
    assert result["summary"] == "Your sugar level is slightly high."
    assert result["risk_flags"][0]["status"] == "High"

@pytest.mark.asyncio
async def test_clean_json(mcp_pipeline):
    raw_json = "```json\n{\"key\": \"value\"}\n```"
    cleaned = mcp_pipeline._clean_json(raw_json)
    assert cleaned == {"key": "value"}

    invalid_json = "Not a JSON"
    cleaned_invalid = mcp_pipeline._clean_json(invalid_json)
    assert cleaned_invalid == {}
