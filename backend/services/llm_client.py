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
            # 1. First choice: Pydantic settings
            # 2. Second choice: Environment variable directly
            # 3. Third choice: vertexai.init() which falls back to ADC or gcloud config
            project = self.project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
            location = self.location or os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
            
            logger.info(f"Initializing Vertex AI. Project: {project or 'None (ADC)'}, Location: {location}")
            
            vertexai.init(project=project, location=location)
            # Use json mode to guarantee JSON output
            self.model = GenerativeModel(
                model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            self.initialized = True
            logger.info(f"Vertex AI successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}", exc_info=True)
            self.model = None
            self.initialized = False

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
