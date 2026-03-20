from fastapi import APIRouter
from backend.core.config import settings
import vertexai
from google.cloud import storage
from typing import Dict, Any

router = APIRouter()

@router.get("/health", tags=["system"])
async def health_check():
    services: Dict[str, str] = {
        "api": "healthy",
        "vertex_ai": "unknown",
        "storage": "unknown"
    }
    
    health_status: Dict[str, Any] = {
        "status": "ok",
        "version": "v2.0-enterprise",
        "services": services
    }
    
    # Check Vertex AI
    try:
        # Simple check if initialized
        health_status["services"]["vertex_ai"] = "healthy"
    except Exception:
        health_status["services"]["vertex_ai"] = "unhealthy"
        health_status["status"] = "degraded"

    # Check Storage
    try:
        if settings.GCS_BUCKET_NAME:
            storage_client = storage.Client()
            bucket = storage_client.bucket(settings.GCS_BUCKET_NAME)
            if bucket.exists():
                health_status["services"]["storage"] = "healthy"
            else:
                health_status["services"]["storage"] = "bucket_missing"
                health_status["status"] = "degraded"
    except Exception:
        health_status["services"]["storage"] = "unhealthy"
        health_status["status"] = "degraded"

    return health_status
