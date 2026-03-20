import os
import json
import logging
import asyncio
import vertexai
from vertexai.generative_models import GenerativeModel
from backend.core.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_CLOUD_LOCATION
        
        try:
            # Attempt initialization. vertexai.init will handle None project by looking at ADC/gcloud config.
            vertexai.init(project=self.project_id, location=self.location)
            # Use json mode to guarantee JSON output
            self.model = GenerativeModel(
                model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            logger.info(f"Vertex AI initialized with project: {self.project_id or 'ADC Default'}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            self.model = None

    async def generate_json(self, prompt: str, fallback_data: dict) -> dict:
        """Executes LLM call and returns strictly parsed JSON dictionary."""
        if not self.model:
            logger.warning("Vertex AI not initialized. Returning fallback strictly-typed JSON mock data.")
            return fallback_data
            
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.model.generate_content, prompt)
            
            # Vertex AI JSON mode guarantees parsable JSON string
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"LLM Generation failed or failed to parse JSON: {e}")
            return fallback_data
