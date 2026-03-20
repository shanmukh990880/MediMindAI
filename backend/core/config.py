from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "MediBrief AI Enterprise API"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    # Environment
    ENV: str = "development"
    
    # GCP Configurations
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    DOCUMENT_AI_PROCESSOR_ID: Optional[str] = None
    GCS_BUCKET_NAME: Optional[str] = None
    
    # Security
    MAX_UPLOAD_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_MIME_TYPES: list[str] = ["application/pdf"]

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=[".env", "backend/.env"]
    )

settings = Settings()
